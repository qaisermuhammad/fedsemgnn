
# ppo_semantic.py
from src.algorithms.PPO import PPO, Memory

class PPO_Semantic(PPO):
    """
    Extend your PPO class by giving each agent its own Memory buffer.
    """
    def __init__(self, state_dim, action_dim, hidden_dim=16,
                 dropout_prob=0.5, entropy_coef=0.5, async_lr=0.01):
        super().__init__(state_dim, action_dim, hidden_dim,
                         dropout_prob, entropy_coef, async_lr)
        self.memory = Memory()
