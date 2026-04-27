# online_semantic_learning.py
"""
Online/Continual Semantic Learning Module for FedSemGNN

Addresses Supervisor Suggestion #3: Replace static semantic embeddings 
with adaptive learning to capture emerging service semantics.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import deque, defaultdict
import os
import time
import json
import os
import logging
from .config import SEMANTIC_CONFIG

logger = logging.getLogger(__name__)


class OnlineSemanticEncoder(nn.Module):
    """
    Continual learning module that adapts semantic embeddings online.
    Uses experience replay and elastic weight consolidation (EWC) to
    prevent catastrophic forgetting while learning new service types.
    """
    
    def __init__(
        self,
        input_dim: int = 128,
        hidden_dim: int = 64,
        embedding_dim: int = 16,
        memory_size: int = 1000,
        ewc_lambda: float = 0.4,
        learning_rate: float = 1e-4,
    ):
        super().__init__()
        
        self.input_dim = input_dim
        self.embedding_dim = embedding_dim
        self.memory_size = memory_size
        self.ewc_lambda = ewc_lambda
        
        # Neural network layers
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, embedding_dim),
            nn.Tanh()  # Normalize embeddings
        )
        
        # Continual learning components
        self.experience_buffer = deque(maxlen=memory_size)
        self.service_type_counts = defaultdict(int)
        self.fisher_information = {}
        self.optimal_params = {}
        
        # Optimizer
        self.optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate)
        
        # Adaptation tracking
        self.adaptation_history = []
        self.seen_service_types = set()
        
    def forward(self, service_features: torch.Tensor) -> torch.Tensor:
        """Generate semantic embedding for service features."""
        return self.encoder(service_features)
    
    def extract_service_features(self, service_obj) -> torch.Tensor:
        """
        Extract high-dimensional features from service object.
        This replaces the simple random vector in semantic_utils.py
        """
        # NOTE: In the simulator, we may receive either Service-like objects
        # or EdgeServer-like objects (for node capability profiles).
        obj_type = type(service_obj).__name__
        features: list[float] = []

        if obj_type == "EdgeServer":
            features.extend([
                float(getattr(service_obj, 'cpu', 0.0)),
                float(getattr(service_obj, 'memory', 0.0)),
                float(getattr(service_obj, 'disk', 0.0)),
                float(getattr(service_obj, 'bandwidth', 0.0)),
            ])
            # A lightweight capability signature (stable in simulation)
            features.extend([
                float(getattr(service_obj, 'get_power_consumption', lambda: 0.0)()),
                float(getattr(service_obj, 'ongoing_migrations', 0.0)),
            ])

            # Pad/truncate to input_dim
            while len(features) < self.input_dim:
                features.append(0.0)
            features = features[: self.input_dim]

            device = next(self.parameters()).device
            return torch.tensor(features, dtype=torch.float32, device=device)
        
        # Basic service properties
        features.extend([
            getattr(service_obj, 'cpu_demand', 1.0),
            getattr(service_obj, 'memory_demand', 1.0),
            getattr(service_obj, 'disk_demand', 1.0),
            getattr(service_obj, 'network_demand', 1.0),
        ])
        
        # Service type indicators (one-hot-like encoding)
        service_type = getattr(service_obj, 'service_type', 'unknown')
        type_features = self._encode_service_type(service_type)
        features.extend(type_features)
        
        # Temporal features
        current_time = time.time()
        features.extend([
            current_time % 86400,  # time of day
            (current_time % 604800) / 604800,  # day of week
        ])
        
        # Workload characteristics
        features.extend([
            getattr(service_obj, 'priority', 0.5),
            getattr(service_obj, 'latency_sensitivity', 0.5),
            getattr(service_obj, 'data_locality_requirement', 0.0),
        ])
        
        # Pad or truncate to input_dim
        while len(features) < self.input_dim:
            features.append(0.0)
        features = features[:self.input_dim]
        
        # Ensure tensor is on the same device as the model
        device = next(self.parameters()).device
        return torch.tensor(features, dtype=torch.float32, device=device)
    
    def _encode_service_type(self, service_type: str) -> List[float]:
        """Generate features for service type (expandable for new types)."""
        # Common service types in edge computing
        known_types = {
            'iot_sensor': [1, 0, 0, 0, 0],
            'video_stream': [0, 1, 0, 0, 0],
            'ml_inference': [0, 0, 1, 0, 0],
            'ar_vr': [0, 0, 0, 1, 0],
            'autonomous_vehicle': [0, 0, 0, 0, 1],
        }
        
        if service_type in known_types:
            return known_types[service_type]
        else:
            # New service type - learn online
            return [0, 0, 0, 0, 0]  # Will be learned
    
    def update_embedding(self, service_obj, placement_feedback: Dict) -> np.ndarray:
        """
        Online learning update based on placement feedback.
        
        Args:
            service_obj: Service object
            placement_feedback: Dict with 'reward', 'latency', 'success'
        
        Returns:
            Updated semantic embedding as numpy array
        """
        try:
            # Extract features and current embedding
            features = self.extract_service_features(service_obj)
            current_embedding = self.forward(features.unsqueeze(0)).squeeze()
            
            # Store experience for replay
            experience = {
                'features': features.clone().detach(),
                'embedding': current_embedding.clone().detach(),
                'feedback': placement_feedback.copy(),
                'timestamp': time.time()
            }
            self.experience_buffer.append(experience)
            
            # Update service type counts
            service_type = getattr(service_obj, 'service_type', 'unknown')
            self.service_type_counts[service_type] += 1
            
            # Detect new service type
            if service_type not in self.seen_service_types:
                self.seen_service_types.add(service_type)
                self._on_new_service_type(service_type)
            
            # Perform online learning update
            self._perform_continual_update(features, placement_feedback)
            
            # Return updated embedding as numpy array
            with torch.no_grad():
                updated_embedding = self.forward(features.unsqueeze(0)).squeeze()
            
            return updated_embedding.cpu().numpy()
            
        except Exception as e:
            logger.error(f"Error in update_embedding: {e}")
            # Fallback: return a basic embedding
            return np.random.randn(self.embedding_dim).astype(np.float32) * 0.1
    
    def _on_new_service_type(self, service_type: str):
        """Handle discovery of new service type."""
        print(f"[OnlineSemanticLearning] New service type detected: {service_type}")
        
        # Compute Fisher Information Matrix for EWC
        self._compute_fisher_information()
        
        # Store current optimal parameters
        self.optimal_params = {name: param.clone() 
                              for name, param in self.named_parameters()}
        
        # Log adaptation event
        self.adaptation_history.append({
            'timestamp': time.time(),
            'event': 'new_service_type',
            'service_type': service_type,
            'total_types': len(self.seen_service_types)
        })
    
    def _compute_fisher_information(self):
        """Compute Fisher Information Matrix for EWC."""
        if len(self.experience_buffer) < 10:
            return
        
        self.fisher_information = {}
        for name, param in self.named_parameters():
            self.fisher_information[name] = torch.zeros_like(param)
        
        # Sample from experience buffer
        sample_size = min(100, len(self.experience_buffer)) if self.experience_buffer else 0
        samples = np.random.choice(len(self.experience_buffer), sample_size, replace=False)
        
        for idx in samples:
            experience = self.experience_buffer[idx]
            features = experience['features'].unsqueeze(0)
            
            # Forward pass
            embedding = self.forward(features)
            
            # Compute loss (reconstruction + reward-based)
            loss = F.mse_loss(embedding, experience['embedding'].unsqueeze(0))
            
            # Backward pass to get gradients
            self.optimizer.zero_grad()
            loss.backward()
            
            # Accumulate Fisher Information
            for name, param in self.named_parameters():
                if param.grad is not None:
                    self.fisher_information[name] += param.grad ** 2
        
        # Normalize Fisher Information
        for name in self.fisher_information:
            self.fisher_information[name] /= sample_size
    
    def _perform_continual_update(self, features: torch.Tensor, 
                                 feedback: Dict):
        """Perform continual learning update with EWC regularization."""
        try:
            self.optimizer.zero_grad()
            
            # Current prediction
            embedding = self.forward(features.unsqueeze(0))
            
            # Compute primary loss (reward-based learning)
            reward = feedback.get('reward', 0.0)
            latency = feedback.get('latency', 1.0)
            success = feedback.get('success', 1.0)
            
            # Get device for tensor creation
            device = embedding.device
            
            # Create target embedding based on feedback (differentiable)
            # Use embedding magnitude as a proxy for learning signal
            embedding_norm = torch.norm(embedding)
            
            # Simple MSE loss against a target embedding magnitude
            target_magnitude = torch.tensor(1.0, dtype=torch.float32, device=device, requires_grad=False)
            if reward > 500:  # Good placement
                target_magnitude = torch.tensor(1.5, dtype=torch.float32, device=device, requires_grad=False)
            elif reward < 100:  # Poor placement
                target_magnitude = torch.tensor(0.5, dtype=torch.float32, device=device, requires_grad=False)
            
            primary_loss = F.mse_loss(embedding_norm, target_magnitude)
            
            # EWC regularization loss
            ewc_loss = torch.tensor(0.0, dtype=torch.float32, device=device)
            if self.fisher_information and self.optimal_params:
                for name, param in self.named_parameters():
                    if name in self.fisher_information:
                        fisher = self.fisher_information[name]
                        optimal = self.optimal_params[name]
                        ewc_loss = ewc_loss + (fisher * (param - optimal) ** 2).sum()
            
            # Combined loss
            total_loss = primary_loss + self.ewc_lambda * ewc_loss
            
            # Ensure the loss requires gradients before backward pass
            if total_loss.requires_grad and torch.is_grad_enabled():
                # Backward pass and update
                total_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.parameters(), 1.0)
                self.optimizer.step()
            else:
                logger.debug("Skipping gradient update: loss does not require gradients or grad disabled")
            
            # Experience replay (mini-batch)
            self._experience_replay()
            
        except Exception as e:
            logger.error(f"Error in continual update: {e}")
            # Continue without update if there's an error
    
    def _experience_replay(self, batch_size: int = 8):
        """Perform experience replay to maintain old knowledge."""
        if len(self.experience_buffer) < batch_size:
            return
        
        # Sample random experiences
        indices = np.random.choice(len(self.experience_buffer), batch_size, replace=False)
        
        batch_features = []
        batch_targets = []
        
        for idx in indices:
            experience = self.experience_buffer[idx]
            batch_features.append(experience['features'])
            batch_targets.append(experience['embedding'])
        
        batch_features = torch.stack(batch_features)
        batch_targets = torch.stack(batch_targets)
        
        # Forward pass
        predictions = self.forward(batch_features)
        
        # Reconstruction loss
        replay_loss = F.mse_loss(predictions, batch_targets)
        
        # Update
        self.optimizer.zero_grad()
        replay_loss.backward()
        self.optimizer.step()
    
    def get_adaptation_stats(self) -> Dict:
        """Get statistics about online adaptation."""
        return {
            'total_service_types': len(self.seen_service_types),
            'service_type_distribution': dict(self.service_type_counts),
            'adaptation_events': len(self.adaptation_history),
            'experience_buffer_size': len(self.experience_buffer),
            'recent_adaptations': self.adaptation_history[-5:] if self.adaptation_history else []
        }
    
    def save_model(self, path: str):
        """Save the online learning model and metadata."""
        checkpoint = {
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'fisher_information': self.fisher_information,
            'optimal_params': self.optimal_params,
            'seen_service_types': list(self.seen_service_types),
            'service_type_counts': dict(self.service_type_counts),
            'adaptation_history': self.adaptation_history,
            'config': {
                'input_dim': self.input_dim,
                'embedding_dim': self.embedding_dim,
                'memory_size': self.memory_size,
                'ewc_lambda': self.ewc_lambda
            }
        }
        
        torch.save(checkpoint, path)
        print(f"[OnlineSemanticLearning] Model saved to {path}")
    
    def load_model(self, path: str):
        """Load the online learning model and metadata."""
        if not os.path.exists(path):
            print(f"[OnlineSemanticLearning] No checkpoint found at {path}")
            return
        
        checkpoint = torch.load(path)
        
        dim_mismatch = False
        try:
            self.load_state_dict(checkpoint['model_state_dict'])
        except RuntimeError as e:
            # Dimension mismatch when semantic_dim changed — start fresh weights
            dim_mismatch = True
            print(f"[OnlineSemanticLearning] Checkpoint dimension mismatch ({e}); starting with fresh weights.")
        try:
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        except (RuntimeError, ValueError) as e:
            print(f"[OnlineSemanticLearning] Optimizer state mismatch; reinitialising optimizer.")
        if dim_mismatch:
            # Reset EWC state — old fisher/optimal tensors have wrong shapes
            self.fisher_information = {}
            self.optimal_params = {}
        else:
            self.fisher_information = checkpoint.get('fisher_information', {})
            self.optimal_params = checkpoint.get('optimal_params', {})
        self.seen_service_types = set(checkpoint.get('seen_service_types', []))
        self.service_type_counts = defaultdict(int, checkpoint.get('service_type_counts', {}))
        self.adaptation_history = checkpoint.get('adaptation_history', [])
        
        print(f"[OnlineSemanticLearning] Model loaded from {path}")
        print(f"  Known service types: {len(self.seen_service_types)}")
        print(f"  Adaptation events: {len(self.adaptation_history)}")


# Global instance for use in FedSemGNN
online_semantic_encoder = None


def initialize_online_semantic_learning():
    """Initialize the global online semantic learning module."""
    global online_semantic_encoder
    
    if online_semantic_encoder is None:
        # Allow experiment overrides via environment variables (used by sensitivity scripts).
        # Defaults match the manuscript.
        try:
            ewc_lambda = float(os.environ.get("FEDSEMGNN_EWC_LAMBDA", "0.4"))
        except Exception:
            ewc_lambda = 0.4
        try:
            online_lr = float(os.environ.get("FEDSEMGNN_ONLINE_LR", "0.0001"))
        except Exception:
            online_lr = 1e-4

        online_semantic_encoder = OnlineSemanticEncoder(
            input_dim=128,
            embedding_dim=SEMANTIC_CONFIG.get("semantic_dim", 16),
            memory_size=1000,
            ewc_lambda=ewc_lambda,
            learning_rate=online_lr,
        )
        
        # Try to load existing model
        checkpoint_path = "results/online_semantic_model.pth"
        online_semantic_encoder.load_model(checkpoint_path)

        # Optimizer state in checkpoints may override the requested LR.
        # Enforce the configured online LR after loading.
        try:
            for pg in online_semantic_encoder.optimizer.param_groups:
                pg["lr"] = online_lr
        except Exception:
            pass
        
        print("[OnlineSemanticLearning] Initialized online semantic learning module")


def extract_semantic_vector_online(service_obj, placement_feedback: Optional[Dict] = None):
    """
    Enhanced semantic vector extraction with online learning.
    
    This replaces the static semantic_utils.extract_semantic_vector() function.
    """
    global online_semantic_encoder
    
    try:
        if online_semantic_encoder is None:
            initialize_online_semantic_learning()
        
        if placement_feedback is not None:
            # Update model based on feedback and return numpy array
            return online_semantic_encoder.update_embedding(service_obj, placement_feedback)
        else:
            # Just extract current embedding as numpy array
            features = online_semantic_encoder.extract_service_features(service_obj)
            with torch.no_grad():
                embedding = online_semantic_encoder.forward(features.unsqueeze(0)).squeeze()
            return embedding.cpu().numpy()
            
    except Exception as e:
        logger.error(f"Error in extract_semantic_vector_online: {e}")
        # Fallback to basic semantic vector
        return np.random.randn(SEMANTIC_CONFIG.get("semantic_dim", 16)) * 0.1


def save_online_semantic_model():
    """Save the current online semantic model."""
    global online_semantic_encoder
    
    if online_semantic_encoder is not None:
        os.makedirs("results", exist_ok=True)
        checkpoint_path = "results/online_semantic_model.pth"
        online_semantic_encoder.save_model(checkpoint_path)


def get_online_semantic_stats():
    """Get adaptation statistics."""
    global online_semantic_encoder
    
    if online_semantic_encoder is not None:
        return online_semantic_encoder.get_adaptation_stats()
    else:
        return {}


# Backward compatibility function
def extract_semantic_vector(obj):
    """Backward compatible wrapper for existing code."""
    return extract_semantic_vector_online(obj)
