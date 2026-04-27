# multi_cluster_fault_tolerance.py
"""
Multi-Cluster Fault Tolerance Module for FedSemGNN

Addresses Supervisor Suggestion #4: Extend fault tolerance beyond single-cluster 
failures to handle simultaneous multi-cluster disruptions with resilience-aware 
reward shaping and proactive redundancy strategies.
"""

import torch
import numpy as np
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, deque
import time
import random
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClusterState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"


@dataclass
class ClusterFailureEvent:
    cluster_id: int
    failure_time: float
    failure_type: str  # 'network', 'power', 'hardware', 'overload'
    severity: float  # 0.0 to 1.0
    estimated_recovery_time: float
    affected_services: Set[int]
    cascade_risk: float  # Risk of causing other failures


class MultiClusterFaultTolerance:
    """
    Handles multi-cluster fault tolerance with:
    1. Proactive failure detection and prediction
    2. Resilience-aware reward shaping
    3. Multi-cluster failover strategies
    4. Cross-cluster redundancy management
    """
    
    def __init__(self, num_clusters: int, redundancy_factor: float = 2.0,
                 cascade_threshold: float = 0.7, recovery_timeout: float = 300.0):
        self.num_clusters = num_clusters
        self.redundancy_factor = redundancy_factor
        self.cascade_threshold = cascade_threshold
        self.recovery_timeout = recovery_timeout
        
        # Cluster state tracking
        self.cluster_states = {i: ClusterState.HEALTHY for i in range(num_clusters)}
        self.cluster_health_scores = {i: 1.0 for i in range(num_clusters)}
        self.cluster_failure_history = defaultdict(list)
        
        # Service placement tracking
        self.service_cluster_mapping = {}  # service_id -> cluster_id
        self.cluster_service_mapping = defaultdict(set)  # cluster_id -> set(service_ids)
        self.redundant_placements = defaultdict(set)  # service_id -> set(backup_cluster_ids)
        
        # Failure prediction and monitoring
        self.failure_predictors = {}  # cluster_id -> failure probability
        self.cluster_metrics_history = defaultdict(lambda: deque(maxlen=100))
        
        # Recovery and failover state
        self.active_failures = {}  # cluster_id -> ClusterFailureEvent
        self.recovery_plans = {}  # cluster_id -> recovery plan
        self.failover_mappings = {}  # failed_cluster_id -> backup_cluster_id
        
        # Resilience metrics
        self.resilience_score = 1.0
        self.cascade_events = []
        self.recovery_times = []
        
        logger.info(f"Initialized Multi-Cluster Fault Tolerance for {num_clusters} clusters")
    
    def update_cluster_metrics(self, cluster_id: int, metrics: Dict):
        """Update cluster health metrics and detect potential failures."""
        timestamp = time.time()
        
        # Store metrics
        self.cluster_metrics_history[cluster_id].append({
            'timestamp': timestamp,
            'metrics': metrics.copy()
        })
        
        # Calculate health score
        health_score = self._calculate_cluster_health(cluster_id, metrics)
        self.cluster_health_scores[cluster_id] = health_score
        
        # Update cluster state based on health
        self._update_cluster_state(cluster_id, health_score)
        
        # Predict failure probability
        failure_prob = self._predict_cluster_failure(cluster_id)
        self.failure_predictors[cluster_id] = failure_prob
        
        # Trigger proactive measures if needed
        if failure_prob > 0.6 or health_score < 0.3:
            self._trigger_proactive_measures(cluster_id, failure_prob, health_score)
    
    def _calculate_cluster_health(self, cluster_id: int, metrics: Dict) -> float:
        """Calculate normalized health score for a cluster."""
        weights = {
            'cpu_utilization': 0.25,
            'memory_utilization': 0.25,
            'power_consumption': 0.2,
            'network_latency': 0.15,
            'error_rate': 0.15
        }
        
        health_components = {}
        
        # CPU health (lower utilization = better, but not too low)
        cpu_util = metrics.get('cpu_utilization', 0.5)
        health_components['cpu'] = 1.0 - abs(cpu_util - 0.6)  # Optimal around 60%
        
        # Memory health
        mem_util = metrics.get('memory_utilization', 0.5)
        health_components['memory'] = max(0.0, 1.0 - mem_util)
        
        # Power health (normalized)
        power = metrics.get('power_consumption', 1000.0)
        max_power = metrics.get('max_power_capacity', 2000.0)
        health_components['power'] = max(0.0, 1.0 - power / max_power)
        
        # Network health
        latency = metrics.get('network_latency', 10.0)  # ms
        health_components['network'] = max(0.0, 1.0 - latency / 100.0)
        
        # Error rate health
        error_rate = metrics.get('error_rate', 0.0)
        health_components['error'] = max(0.0, 1.0 - error_rate * 10.0)
        
        # Weighted health score
        total_health = sum(
            weights.get(component.replace('_health', ''), 0.2) * score
            for component, score in health_components.items()
        )
        return max(0.0, min(1.0, total_health))

    def _predict_cluster_failure(self, cluster_id: int) -> float:
        """Predict probability of cluster failure using historical trends."""
        history = self.cluster_metrics_history[cluster_id]
        if len(history) < 10:
            return 0.1  # Low probability for insufficient data
        
        # Analyze trends
        recent_scores = [self.cluster_health_scores[cluster_id] for _ in range(min(10, len(history)))]
        
        # Health trend (declining = higher failure risk)
        if len(recent_scores) >= 3:
            trend = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
            trend_risk = max(0.0, -trend * 2.0)  # Negative trend increases risk
        else:
            trend_risk = 0.0

        # Current health risk
        current_health = self.cluster_health_scores[cluster_id]
        health_risk = 1.0 - current_health

        # Historical failure frequency
        recent_failures = [f for f in self.cluster_failure_history[cluster_id] 
                           if time.time() - f.failure_time < 3600]  # Last hour
        # Defensive patch for min() on recent_failures
        frequency_risk = min(1.0, len(recent_failures) * 0.2) if recent_failures is not None else 0.0

        # Combined failure probability
        failure_prob = (0.4 * health_risk + 0.3 * trend_risk + 0.3 * frequency_risk)
        
        return max(0.0, min(1.0, failure_prob))
    
    def _update_cluster_state(self, cluster_id: int, health_score: float):
        """Update cluster state based on health score."""
        current_state = self.cluster_states[cluster_id]
        
        if health_score >= 0.8:
            new_state = ClusterState.HEALTHY
        elif health_score >= 0.5:
            new_state = ClusterState.DEGRADED
        elif health_score >= 0.2:
            new_state = ClusterState.RECOVERING if current_state == ClusterState.FAILED else ClusterState.DEGRADED
        else:
            new_state = ClusterState.FAILED
        
        if new_state != current_state:
            logger.warning(f"Cluster {cluster_id} state changed: {current_state.value} -> {new_state.value}")
            self.cluster_states[cluster_id] = new_state
            
            if new_state == ClusterState.FAILED:
                self._handle_cluster_failure(cluster_id)
            elif new_state == ClusterState.HEALTHY and current_state in [ClusterState.FAILED, ClusterState.RECOVERING]:
                self._handle_cluster_recovery(cluster_id)
    
    def _trigger_proactive_measures(self, cluster_id: int, failure_prob: float, health_score: float):
        """Trigger proactive measures before cluster failure."""
        logger.info(f"Triggering proactive measures for cluster {cluster_id} (failure_prob={failure_prob:.3f}, health={health_score:.3f})")
        
        # 1. Increase redundancy for critical services
        self._increase_service_redundancy(cluster_id)
        
        # 2. Pre-migrate non-critical services
        if failure_prob > 0.8:
            self._preemptive_service_migration(cluster_id)
        
        # 3. Prepare backup clusters
        self._prepare_backup_clusters(cluster_id)
        
        # 4. Alert monitoring systems
        self._send_proactive_alert(cluster_id, failure_prob, health_score)
    
    def _handle_cluster_failure(self, cluster_id: int):
        """Handle cluster failure with multi-cluster failover."""
        logger.error(f"Handling failure of cluster {cluster_id}")
        
        # Create failure event
        failure_event = ClusterFailureEvent(
            cluster_id=cluster_id,
            failure_time=time.time(),
            failure_type=self._determine_failure_type(cluster_id),
            severity=1.0 - self.cluster_health_scores[cluster_id],
            estimated_recovery_time=self._estimate_recovery_time(cluster_id),
            affected_services=self.cluster_service_mapping[cluster_id].copy(),
            cascade_risk=self._calculate_cascade_risk(cluster_id)
        )
        
        self.active_failures[cluster_id] = failure_event
        self.cluster_failure_history[cluster_id].append(failure_event)
        
        # Execute failover strategy
        self._execute_multi_cluster_failover(cluster_id, failure_event)
        
        # Check for cascade failures
        self._check_cascade_failures(cluster_id, failure_event)
        
        # Update resilience metrics
        self._update_resilience_metrics(failure_event)
    
    def _execute_multi_cluster_failover(self, failed_cluster_id: int, failure_event: ClusterFailureEvent):
        """Execute multi-cluster failover for affected services."""
        affected_services = failure_event.affected_services
        
        if not affected_services:
            return
        
        logger.info(f"Executing failover for {len(affected_services)} services from cluster {failed_cluster_id}")
        
        # Find backup clusters
        backup_clusters = self._select_backup_clusters(failed_cluster_id, len(affected_services))
        
        if not backup_clusters:
            logger.error(f"No available backup clusters for failover from cluster {failed_cluster_id}")
            return
        
        # Distribute services across backup clusters
        service_list = list(affected_services)
        services_per_cluster = len(service_list) // len(backup_clusters)
        
        for i, backup_cluster_id in enumerate(backup_clusters):
            start_idx = i * services_per_cluster
            end_idx = start_idx + services_per_cluster if i < len(backup_clusters) - 1 else len(service_list)
            
            services_to_migrate = service_list[start_idx:end_idx]
            
            for service_id in services_to_migrate:
                self._migrate_service_to_cluster(service_id, failed_cluster_id, backup_cluster_id)
        
        # Record failover mapping
        self.failover_mappings[failed_cluster_id] = backup_clusters
        
        logger.info(f"Failover completed: cluster {failed_cluster_id} -> clusters {backup_clusters}")
    
    def _select_backup_clusters(self, failed_cluster_id: int, num_services: int) -> List[int]:
        """Select optimal backup clusters for failover."""
        # Get healthy clusters
        healthy_clusters = [
            cid for cid, state in self.cluster_states.items()
            if cid != failed_cluster_id and state in [ClusterState.HEALTHY, ClusterState.DEGRADED]
        ]
        
        if not healthy_clusters:
            return []
        
        # Sort by health score and available capacity
        cluster_scores = []
        for cluster_id in healthy_clusters:
            health = self.cluster_health_scores[cluster_id]
            current_load = len(self.cluster_service_mapping[cluster_id])
            capacity_score = max(0.0, 1.0 - current_load / 100.0)  # Assume max 100 services per cluster
            
            combined_score = 0.6 * health + 0.4 * capacity_score
            cluster_scores.append((cluster_id, combined_score))
        
        # Sort by score (descending)
        cluster_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top clusters based on redundancy factor
        # Defensive patch for min() on backup_clusters
        num_backup_clusters = min(len(healthy_clusters), max(1, int(self.redundancy_factor))) if healthy_clusters else 1
        backup_clusters = [cluster_id for cluster_id, _ in cluster_scores[:num_backup_clusters]]

        return backup_clusters
    
    def _migrate_service_to_cluster(self, service_id: int, from_cluster: int, to_cluster: int):
        """Migrate a service from failed cluster to backup cluster."""
        # Update mappings
        if service_id in self.service_cluster_mapping:
            del self.service_cluster_mapping[service_id]
        
        self.cluster_service_mapping[from_cluster].discard(service_id)
        
        self.service_cluster_mapping[service_id] = to_cluster
        self.cluster_service_mapping[to_cluster].add(service_id)
        
        # Add to redundant placements for future protection
        self.redundant_placements[service_id].add(to_cluster)
        
        logger.debug(f"Migrated service {service_id}: cluster {from_cluster} -> {to_cluster}")
    
    def _check_cascade_failures(self, failed_cluster_id: int, failure_event: ClusterFailureEvent):
        """Check for potential cascade failures and take preventive action."""
        if failure_event.cascade_risk < self.cascade_threshold:
            return
        
        logger.warning(f"High cascade risk ({failure_event.cascade_risk:.3f}) detected from cluster {failed_cluster_id}")
        
        # Identify at-risk clusters
        at_risk_clusters = []
        for cluster_id in range(self.num_clusters):
            if cluster_id == failed_cluster_id or self.cluster_states[cluster_id] == ClusterState.FAILED:
                continue
            
            # Check proximity/dependency to failed cluster
            cascade_prob = self._calculate_cascade_probability(cluster_id, failed_cluster_id, failure_event)
            
            if cascade_prob > 0.4:
                at_risk_clusters.append((cluster_id, cascade_prob))
        
        # Take preventive measures
        for cluster_id, cascade_prob in at_risk_clusters:
            logger.info(f"Taking preventive measures for at-risk cluster {cluster_id} (cascade_prob={cascade_prob:.3f})")
            self._prevent_cascade_failure(cluster_id, cascade_prob)
    
    def _calculate_cascade_probability(self, cluster_id: int, failed_cluster_id: int, 
                                     failure_event: ClusterFailureEvent) -> float:
        """Calculate probability of cascade failure."""
        # Factors affecting cascade probability:
        
        # 1. Current health of the cluster
        health_factor = 1.0 - self.cluster_health_scores[cluster_id]
        
        # 2. Load increase due to failover
        if cluster_id in self.failover_mappings.get(failed_cluster_id, []):
            load_factor = 0.5  # Increased load from failover
        else:
            load_factor = 0.0
        
        # 3. Failure type correlation
        failure_type_factor = 0.3 if failure_event.failure_type in ['power', 'network'] else 0.1
        
        # 4. Geographic/logical proximity (simplified)
        proximity_factor = 0.2 if abs(cluster_id - failed_cluster_id) <= 2 else 0.0
        
        cascade_prob = (0.4 * health_factor + 0.3 * load_factor + 
                       0.2 * failure_type_factor + 0.1 * proximity_factor)
        
        return max(0.0, min(1.0, cascade_prob))
    
    def _prevent_cascade_failure(self, cluster_id: int, cascade_prob: float):
        """Take measures to prevent cascade failure."""
        # Reduce load on at-risk cluster
        services_to_move = list(self.cluster_service_mapping[cluster_id])
        num_to_move = int(len(services_to_move) * cascade_prob * 0.5)
        
        if num_to_move > 0:
            # Move some services to other healthy clusters
            for service_id in random.sample(services_to_move, min(num_to_move, len(services_to_move))):
                backup_clusters = self._select_backup_clusters(cluster_id, 1)
                if backup_clusters:
                    self._migrate_service_to_cluster(service_id, cluster_id, backup_clusters[0])
    
    def calculate_resilience_aware_reward(self, base_reward: float, 
                                        cluster_distributions: Dict[int, int]) -> float:
        """
        Calculate resilience-aware reward that penalizes single points of failure
        and rewards distributed, fault-tolerant placements.
        """
        # Base resilience score
        resilience_bonus = 0.0
        
        # 1. Distribution bonus - reward spreading services across clusters
        total_services = sum(cluster_distributions.values())
        if total_services > 0:
            # Calculate entropy of distribution
            distribution_entropy = 0.0
            for count in cluster_distributions.values():
                if count > 0:
                    p = count / total_services
                    distribution_entropy -= p * np.log2(p)
            
            # Normalize entropy (max entropy for uniform distribution)
            max_entropy = np.log2(len(cluster_distributions))
            if max_entropy > 0:
                normalized_entropy = distribution_entropy / max_entropy
                resilience_bonus += 100.0 * normalized_entropy  # Up to 100 points bonus
        
        # 2. Redundancy bonus - reward services with backup placements
        redundancy_score = 0.0
        # Defensive patch for min() on backup_clusters in redundancy_score
        for service_id, backup_clusters in self.redundant_placements.items():
            if len(backup_clusters) > 1:
                redundancy_score += 10.0 * min(len(backup_clusters), 3) if backup_clusters else 0  # Diminishing returns
        
        resilience_bonus += redundancy_score
        
        # 3. Health penalty - penalize placing services on unhealthy clusters
        health_penalty = 0.0
        for cluster_id, service_count in cluster_distributions.items():
            cluster_health = self.cluster_health_scores.get(cluster_id, 1.0)
            health_penalty += service_count * (1.0 - cluster_health) * 50.0
        
        # 4. Failure penalty - penalize placing services on recently failed clusters
        failure_penalty = 0.0
        current_time = time.time()
        for cluster_id, service_count in cluster_distributions.items():
            recent_failures = [f for f in self.cluster_failure_history[cluster_id]
                             if current_time - f.failure_time < 1800]  # Last 30 minutes
            failure_penalty += service_count * len(recent_failures) * 25.0
        
        # Calculate final resilience-aware reward
        resilience_aware_reward = (base_reward + resilience_bonus - 
                                 health_penalty - failure_penalty)
        
        # Update resilience score
        self.resilience_score = max(0.0, min(1.0, 
            (resilience_bonus - health_penalty - failure_penalty) / max(100.0, base_reward)))

        return resilience_aware_reward
    
    def get_fault_tolerance_stats(self) -> Dict:
        """Get comprehensive fault tolerance statistics."""
        current_time = time.time()
        
        # Cluster health summary
        health_summary = {
            'healthy': sum(1 for state in self.cluster_states.values() if state == ClusterState.HEALTHY),
            'degraded': sum(1 for state in self.cluster_states.values() if state == ClusterState.DEGRADED),
            'failed': sum(1 for state in self.cluster_states.values() if state == ClusterState.FAILED),
            'recovering': sum(1 for state in self.cluster_states.values() if state == ClusterState.RECOVERING)
        }
        
        # Recent failures
        recent_failures = []
        for cluster_failures in self.cluster_failure_history.values():
            recent_failures.extend([f for f in cluster_failures 
                                  if current_time - f.failure_time < 3600])
        
        # Average recovery time
        completed_recoveries = [f for failures in self.cluster_failure_history.values() 
                              for f in failures if hasattr(f, 'recovery_time')]
        avg_recovery_time = np.mean([f.recovery_time for f in completed_recoveries]) if completed_recoveries else 0.0
        
        return {
            'cluster_health_summary': health_summary,
            'total_clusters': self.num_clusters,
            'resilience_score': self.resilience_score,
            'active_failures': len(self.active_failures),
            'recent_failures_1h': len(recent_failures),
            'total_cascade_events': len(self.cascade_events),
            'average_recovery_time': avg_recovery_time,
            'cluster_health_scores': dict(self.cluster_health_scores),
            'failure_predictions': dict(self.failure_predictors),
            'service_distribution': {cid: len(services) for cid, services in self.cluster_service_mapping.items()},
            'redundant_services': len(self.redundant_placements),
            'failover_mappings': dict(self.failover_mappings)
        }
    
    # Additional helper methods
    def _determine_failure_type(self, cluster_id: int) -> str:
        """Determine the type of failure based on metrics."""
        # Simplified failure type determination
        failure_types = ['network', 'power', 'hardware', 'overload']
        return random.choice(failure_types)  # In real implementation, analyze metrics
    
    def _estimate_recovery_time(self, cluster_id: int) -> float:
        """Estimate recovery time for a failed cluster."""
        # Simplified estimation based on failure history
        historical_times = [300.0, 600.0, 900.0, 1200.0]  # 5-20 minutes
        return random.choice(historical_times)
    
    def _calculate_cascade_risk(self, cluster_id: int) -> float:
        """Calculate risk of cascade failure."""
        # Simplified cascade risk calculation
        return random.uniform(0.2, 0.8)
    
    def _increase_service_redundancy(self, cluster_id: int):
        """Increase redundancy for services in at-risk cluster."""
        services = list(self.cluster_service_mapping[cluster_id])
        for service_id in services[:min(5, len(services))]:  # Top 5 critical services
            backup_clusters = self._select_backup_clusters(cluster_id, 1)
            if backup_clusters:
                self.redundant_placements[service_id].add(backup_clusters[0])
    
    def _preemptive_service_migration(self, cluster_id: int):
        """Preemptively migrate non-critical services."""
        services = list(self.cluster_service_mapping[cluster_id])
        non_critical = services[len(services)//2:]  # Bottom half as non-critical
        
        for service_id in non_critical[:3]:  # Migrate up to 3 services
            backup_clusters = self._select_backup_clusters(cluster_id, 1)
            if backup_clusters:
                self._migrate_service_to_cluster(service_id, cluster_id, backup_clusters[0])
    
    def _prepare_backup_clusters(self, cluster_id: int):
        """Prepare backup clusters for potential failover."""
        # Pre-warm backup clusters, reserve capacity, etc.
        backup_clusters = self._select_backup_clusters(cluster_id, 1)
        logger.info(f"Prepared backup clusters {backup_clusters} for cluster {cluster_id}")
    
    def _send_proactive_alert(self, cluster_id: int, failure_prob: float, health_score: float):
        """Send proactive alert to monitoring systems."""
        logger.warning(f"PROACTIVE ALERT: Cluster {cluster_id} at risk - "
                      f"failure_prob={failure_prob:.3f}, health={health_score:.3f}")
    
    def _handle_cluster_recovery(self, cluster_id: int):
        """Handle cluster recovery."""
        if cluster_id in self.active_failures:
            failure_event = self.active_failures[cluster_id]
            failure_event.recovery_time = time.time() - failure_event.failure_time
            self.recovery_times.append(failure_event.recovery_time)
            del self.active_failures[cluster_id]
            
            logger.info(f"Cluster {cluster_id} recovered after {failure_event.recovery_time:.1f} seconds")
    
    def _update_resilience_metrics(self, failure_event: ClusterFailureEvent):
        """Update overall resilience metrics."""
        # Update resilience score based on failure impact
        impact_factor = len(failure_event.affected_services) / max(1, sum(len(services) for services in self.cluster_service_mapping.values()))
        self.resilience_score *= (1.0 - 0.1 * impact_factor)
        self.resilience_score = max(0.0, self.resilience_score)


# Global instance for use in FedSemGNN
fault_tolerance_manager = None


def initialize_fault_tolerance(num_clusters: int):
    """Initialize the global fault tolerance manager."""
    global fault_tolerance_manager
    
    fault_tolerance_manager = MultiClusterFaultTolerance(
        num_clusters=num_clusters,
        redundancy_factor=2.0,
        cascade_threshold=0.7,
        recovery_timeout=300.0
    )
    
    logger.info(f"Initialized fault tolerance manager for {num_clusters} clusters")


def update_cluster_health(cluster_id: int, metrics: Dict):
    """Update cluster health metrics."""
    global fault_tolerance_manager
    
    if fault_tolerance_manager:
        fault_tolerance_manager.update_cluster_metrics(cluster_id, metrics)


def get_resilience_aware_reward(base_reward: float, cluster_distributions: Dict[int, int]) -> float:
    """Get resilience-aware reward that accounts for fault tolerance."""
    global fault_tolerance_manager
    
    if fault_tolerance_manager:
        return fault_tolerance_manager.calculate_resilience_aware_reward(base_reward, cluster_distributions)
    else:
        return base_reward


def get_fault_tolerance_stats() -> Dict:
    """Get fault tolerance statistics."""
    global fault_tolerance_manager
    
    if fault_tolerance_manager:
        return fault_tolerance_manager.get_fault_tolerance_stats()
    else:
        return {}
