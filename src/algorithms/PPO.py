# PPO.py

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.distributions import Categorical
from src.core.config import DP_CONFIG, PPO_CONFIG
from tenacity import retry, stop_after_attempt

class Memory:
    def __init__(self):
        self.actions = []
        self.states = []
        self.logprobs = []
        self.rewards = []
        self.is_terminals = []

    def clear_memory(self):
        del self.actions[:]
        del self.states[:]
        del self.logprobs[:]
        del self.rewards[:]
        del self.is_terminals[:]

class PrioritizedReplayBuffer:
    def __init__(self, capacity=20000, alpha=0.6):
        self.capacity = capacity
        self.alpha = alpha
        self.buffer = []
        self.priorities = []
        self.pos = 0

    def push(self, transition, error=1.0):
        if len(self.buffer) < self.capacity:
            self.buffer.append(transition)
            self.priorities.append(error)
        else:
            self.buffer[self.pos] = transition
            self.priorities[self.pos] = error
            self.pos = (self.pos + 1) % self.capacity

    def sample(self, batch_size, beta=0.4):
        if len(self.buffer) == 0:
            return [], [], []

        priorities = np.array(self.priorities, dtype=np.float32)
        priorities = np.where(np.isnan(priorities), 0.0, priorities)
        priorities = np.maximum(priorities, 1e-5)
        probs = priorities ** self.alpha
        probs = probs / probs.sum()

        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        samples = [self.buffer[i] for i in indices]
        total = len(self.buffer)
        weights = (total * probs[indices]) ** (-beta)
        weights /= weights.max()
        weights = np.array(weights, dtype=np.float32)
        return samples, indices, weights

    def update_priorities(self, indices, errors):
        for idx, error in zip(indices, errors):
            self.priorities[idx] = error

    def __len__(self):
        return len(self.buffer)

class PPO(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim=16, dropout_prob=0.5, entropy_coef=0.5, async_lr=0.01):
        super(PPO, self).__init__()
        self.actor = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Softmax(dim=-1)
        )
        self.critic = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        # Convert model weights to float16 to reduce memory usage
        self.actor = self.actor.half()
        self.critic = self.critic.half()
        self.optimizer = optim.Adam(self.parameters(), lr=1e-3)
        
        self.replay_buffer = PrioritizedReplayBuffer(
            capacity=PPO_CONFIG.get("buffer_capacity", 20000), alpha=0.6
        )
        self.batch_size = 64
        self.gamma = 0.99
        self.beta = 0.4
        self.epsilon        = PPO_CONFIG.get("clip_epsilon", 0.2)
        self.entropy_coef = PPO_CONFIG.get("entropy_coef", entropy_coef)
        self.lr             = PPO_CONFIG.get("learning_rate", 3e-4)
        self.update_epochs  = PPO_CONFIG.get("update_epochs", 4)


    def forward(self, state):
        action_probs = self.actor(state)
        state_value = self.critic(state)
        return action_probs, state_value

    def select_action(self, state, memory):
        state = torch.FloatTensor(state).unsqueeze(0)
        action_probs, _ = self(state)
        dist = Categorical(action_probs)
        action = dist.sample()
        action_logprob = dist.log_prob(action)
        return action.item(), action_logprob.item(), action_probs.detach().numpy().flatten()

    def evaluate(self, states, actions):
        action_probs, state_values = self(states)
        dist = Categorical(action_probs)
        action_logprobs = dist.log_prob(actions)
        dist_entropy = dist.entropy()
        return action_logprobs, torch.squeeze(state_values), dist_entropy

    def update(self):
        if len(self.replay_buffer) < self.batch_size:
            return

        transitions, indices, weights = self.replay_buffer.sample(self.batch_size, self.beta)
        if len(transitions) == 0:
            return

        states, actions, rewards, next_states, dones, old_logprobs = zip(*transitions)
        states = torch.FloatTensor(np.array(states))
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(np.array(next_states))
        dones = torch.FloatTensor(dones)
        old_logprobs = torch.FloatTensor(old_logprobs)
        weights = torch.FloatTensor(weights)

        action_logprobs, state_values, dist_entropy = self.evaluate(states, actions)
        with torch.no_grad():
            _, next_state_values = self(next_states)
            next_state_values = next_state_values.squeeze()

        targets = rewards + self.gamma * next_state_values * (1 - dones)
        advantages = targets - state_values

        ratios = torch.exp(action_logprobs - old_logprobs)
        surr1 = ratios * advantages
        surr2 = torch.clamp(ratios, 1 - self.epsilon, 1 + self.epsilon) * advantages

        # Defensive patch: torch.min is safe for tensors, but ensure surr1 and surr2 are not empty
        if surr1.numel() == 0 or surr2.numel() == 0:
            policy_loss = torch.tensor(0.0, device=surr1.device)
        else:
            policy_loss = -torch.min(surr1, surr2)
        weighted_policy_loss = (policy_loss * weights).mean()
        value_loss = (weights * (state_values - targets).pow(2)).mean()
        entropy_loss = dist_entropy.mean()

        loss = weighted_policy_loss + 0.5 * value_loss - self.entropy_coef * entropy_loss

        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.parameters(), DP_CONFIG["clip_norm"])
        self.optimizer.step()

        errors = (policy_loss.detach().cpu().numpy() +
                  0.5 * (state_values - targets).pow(2).detach().cpu().numpy())
        self.replay_buffer.update_priorities(indices, errors)

    def get_state(self):
        return self.state_dict()

    def load_state(self, state_dict):
        self.load_state_dict(state_dict)

    @staticmethod
    def federated_average(models, weights=None):
        if weights is None:
            weights = [1.0 / len(models)] * len(models)
        avg_state_dict = {}
        for key in models[0].state_dict().keys():
            avg_state_dict[key] = sum(w * m.state_dict()[key].float() for m, w in zip(models, weights))
        for key in avg_state_dict:
            noise = torch.normal(mean=0, std=DP_CONFIG["noise_scale"], size=avg_state_dict[key].size())
            avg_state_dict[key] += noise
        for model in models:
            model.load_state_dict(avg_state_dict)
        return avg_state_dict

    @retry(stop=stop_after_attempt(3))
    def async_update(self, global_model):
        local_state = self.state_dict()
        global_state = global_model.state_dict()
        for key in local_state:
            updated_param = (1 - self.async_lr) * global_state[key] + self.async_lr * local_state[key]
            global_state[key].copy_(updated_param)
        return global_state

    def add_dp_noise(self):
        for param in self.parameters():
            noise = torch.normal(mean=0, std=DP_CONFIG["noise_scale"], size=param.data.size())
            param.data.add_(noise)

    def compute_loss(self, states, actions, advantages, returns):
        probs = self.actor(states)
        dist = Categorical(probs)
        log_probs = dist.log_prob(actions)
        entropy = dist.entropy().mean()
        values = self.critic(states)
        critic_loss = (returns - values).pow(2).mean()
        actor_loss = -log_probs * advantages
        loss = actor_loss + critic_loss - self.entropy_coef * entropy
        print(f"[DEBUG] PPO Entropy: {entropy.item():.4f}")
        return loss
