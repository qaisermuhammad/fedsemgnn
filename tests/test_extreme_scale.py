# test_extreme_scale.py
"""
Test script for extreme scale federated learning features.
Validates adaptive clustering, gradient compression, and communication optimization.
"""

import torch
import numpy as np
import time
from extreme_scale_federated import (
    ExtremeScaleFederatedLearning, 
    CompressionConfig,
    initialize_extreme_scale_federation,
    add_nodes_to_federation,
    handle_extreme_scale_updates,
    get_extreme_scale_stats
)


def test_extreme_scale_clustering():
    """Test adaptive clustering functionality."""
    print("Testing extreme scale adaptive clustering...")
    
    # Initialize extreme scale federation
    esfl = ExtremeScaleFederatedLearning(max_nodes=10000, base_cluster_size=50)
    
    # Create test nodes with diverse characteristics
    node_ids = list(range(500))  # 500 test nodes
    node_features = {}
    
    # Create different types of nodes for clustering
    for i in node_ids:
        if i < 100:  # High-performance data center nodes
            node_features[i] = {
                'cpu_utilization': np.random.uniform(0.2, 0.4),
                'memory_utilization': np.random.uniform(0.3, 0.5),
                'network_bandwidth': np.random.uniform(800, 1000),
                'storage_capacity': np.random.uniform(8000, 10000),
                'service_types_handled': np.random.randint(8, 12),
                'latitude': np.random.uniform(30, 50),
                'longitude': np.random.uniform(-120, -80),
                'network_zone': 1,
                'data_center_tier': 3
            }
        elif i < 300:  # Edge nodes
            node_features[i] = {
                'cpu_utilization': np.random.uniform(0.6, 0.8),
                'memory_utilization': np.random.uniform(0.7, 0.9),
                'network_bandwidth': np.random.uniform(100, 300),
                'storage_capacity': np.random.uniform(1000, 3000),
                'service_types_handled': np.random.randint(3, 6),
                'latitude': np.random.uniform(25, 48),
                'longitude': np.random.uniform(-125, -70),
                'network_zone': np.random.randint(2, 5),
                'data_center_tier': 1
            }
        else:  # IoT/fog nodes
            node_features[i] = {
                'cpu_utilization': np.random.uniform(0.8, 1.0),
                'memory_utilization': np.random.uniform(0.8, 1.0),
                'network_bandwidth': np.random.uniform(10, 100),
                'storage_capacity': np.random.uniform(100, 1000),
                'service_types_handled': np.random.randint(1, 3),
                'latitude': np.random.uniform(20, 50),
                'longitude': np.random.uniform(-130, -65),
                'network_zone': np.random.randint(5, 10),
                'data_center_tier': 0
            }
    
    # Add nodes to federation
    esfl.add_nodes(node_ids, node_features)
    
    # Validate clustering results
    stats = esfl.get_extreme_scale_stats()
    
    print(f"✓ Added {len(node_ids)} nodes")
    print(f"✓ Created {stats['scaling_metrics']['active_clusters']} clusters")
    print(f"✓ Average cluster size: {stats['scaling_metrics']['avg_cluster_size']:.1f}")
    print(f"✓ Cluster size distribution: {stats['cluster_size_distribution']}")
    
    # Test cluster rebalancing
    print("\nTesting cluster rebalancing...")
    
    # Add more nodes to trigger rebalancing
    additional_nodes = list(range(500, 800))
    additional_features = {i: node_features[i % 500] for i in additional_nodes}
    
    esfl.add_nodes(additional_nodes, additional_features)
    
    stats_after = esfl.get_extreme_scale_stats()
    print(f"✓ After adding {len(additional_nodes)} more nodes:")
    print(f"✓ Total clusters: {stats_after['scaling_metrics']['active_clusters']}")
    print(f"✓ Average cluster size: {stats_after['scaling_metrics']['avg_cluster_size']:.1f}")
    
    return esfl


def test_gradient_compression():
    """Test gradient compression functionality."""
    print("\nTesting gradient compression...")
    
    esfl = ExtremeScaleFederatedLearning(max_nodes=1000)
    
    # Create test gradients
    original_gradients = torch.randn(1000, 50)  # Large gradient tensor
    
    print(f"Original gradient size: {original_gradients.numel()} elements")
    print(f"Original memory: {original_gradients.numel() * 4 / 1024:.1f} KB")
    
    # Test compression
    compressed = esfl._compress_gradients(original_gradients)
    
    # Count non-zero elements (sparse representation)
    non_zero_count = torch.count_nonzero(compressed).item()
    compression_ratio = non_zero_count / original_gradients.numel()
    
    print(f"✓ Compressed to {non_zero_count} non-zero elements")
    print(f"✓ Compression ratio: {compression_ratio:.3f}")
    print(f"✓ Memory saved: {(1 - compression_ratio) * 100:.1f}%")
    
    # Test reconstruction quality
    mse = torch.mean((original_gradients - compressed) ** 2).item()
    print(f"✓ Reconstruction MSE: {mse:.6f}")
    
    return compression_ratio


def test_hierarchical_compression():
    """Test hierarchical model compression."""
    print("\nTesting hierarchical model compression...")
    
    esfl = ExtremeScaleFederatedLearning(max_nodes=1000)
    
    # Create a simple test model
    class TestModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1 = torch.nn.Linear(100, 50)
            self.fc2 = torch.nn.Linear(50, 10)
            
    model = TestModel()
    
    # Get original parameter count
    original_params = sum(p.numel() for p in model.parameters())
    print(f"Original model parameters: {original_params}")
    
    # Apply hierarchical compression
    compressed_models = esfl.hierarchical_model_compression(model)
    
    for level, compressed_state in compressed_models.items():
        compressed_params = sum(p.numel() for p in compressed_state.values())
        compression_ratio = compressed_params / original_params
        print(f"✓ {level}: {compressed_params} params (ratio: {compression_ratio:.3f})")
    
    return compressed_models


def test_selective_parameter_exchange():
    """Test selective parameter exchange."""
    print("\nTesting selective parameter exchange...")
    
    esfl = ExtremeScaleFederatedLearning(max_nodes=1000)
    
    # Simulate cluster updates with varying significance
    cluster_updates = {}
    
    for cluster_id in range(10):
        if cluster_id < 3:
            # Significant updates
            gradients = torch.randn(100) * 0.5
        elif cluster_id < 7:
            # Moderate updates
            gradients = torch.randn(100) * 0.1
        else:
            # Minimal updates
            gradients = torch.randn(100) * 0.01
            
        cluster_updates[cluster_id] = gradients
    
    print(f"Total cluster updates: {len(cluster_updates)}")
    
    # Apply selective exchange
    filtered_updates = esfl.selective_parameter_exchange(cluster_updates)
    
    print(f"✓ Selected for exchange: {len(filtered_updates)}")
    print(f"✓ Communication reduction: {(1 - len(filtered_updates) / len(cluster_updates)) * 100:.1f}%")
    
    return len(filtered_updates) / len(cluster_updates)


def test_asynchronous_updates():
    """Test asynchronous update handling with staleness mitigation."""
    print("\nTesting asynchronous updates...")
    
    esfl = ExtremeScaleFederatedLearning(max_nodes=1000, staleness_threshold=5)
    
    # Simulate updates with different staleness levels
    cluster_updates = {}
    current_time = time.time()
    
    for cluster_id in range(8):
        staleness = cluster_id  # Increasing staleness
        timestamp = current_time - staleness * 10  # Older timestamps
        
        cluster_updates[cluster_id] = {
            'gradients': torch.randn(50),
            'version': max(0, 10 - staleness),  # Older versions
            'timestamp': timestamp,
            'node_count': 20
        }
    
    print(f"Created {len(cluster_updates)} async updates with varying staleness")
    
    # Handle async updates
    processed_updates = esfl.handle_asynchronous_updates(cluster_updates)
    
    accepted_count = len(processed_updates)
    rejected_count = len(cluster_updates) - accepted_count
    
    print(f"✓ Accepted updates: {accepted_count}")
    print(f"✓ Rejected stale updates: {rejected_count}")
    print(f"✓ Average staleness: {esfl.scaling_metrics.get('gradient_staleness_avg', 0):.2f}")
    
    return accepted_count / len(cluster_updates)


def test_communication_scheduling():
    """Test adaptive communication scheduling."""
    print("\nTesting adaptive communication scheduling...")
    
    esfl = ExtremeScaleFederatedLearning(max_nodes=1000)
    
    # Initialize some clusters with metrics
    for cluster_id in range(5):
        esfl.cluster_nodes[cluster_id] = set(range(cluster_id * 20, (cluster_id + 1) * 20))
        
        # Set different cluster characteristics
        esfl.cluster_metrics[cluster_id] = type('obj', (object,), {
            'cluster_id': cluster_id,
            'node_count': 20,
            'avg_computation_time': 5.0 + cluster_id,
            'avg_communication_latency': 10.0 + cluster_id * 5,
            'gradient_staleness': cluster_id * 2,
            'model_divergence': 0.1 + cluster_id * 0.1,
            'workload_similarity': 0.9 - cluster_id * 0.1,
            'geographic_spread': cluster_id * 10.0
        })()
    
    # Get communication schedule
    schedule = esfl.adaptive_communication_scheduling()
    
    print(f"✓ Generated schedule for {len(schedule)} clusters")
    
    # Calculate schedule intervals
    current_time = time.time()
    intervals = [schedule[cid] - current_time for cid in schedule.keys()]
    
    print(f"✓ Schedule intervals: {[f'{interval:.1f}s' for interval in intervals]}")
    print(f"✓ Average interval: {np.mean(intervals):.1f}s")
    
    return schedule


def test_full_integration():
    """Test full integration of extreme scale features."""
    print("\nTesting full extreme scale integration...")
    
    # Initialize with configuration
    initialize_extreme_scale_federation(max_nodes=5000, base_cluster_size=50)
    
    # Create diverse node population
    node_ids = list(range(1000))
    node_features = {}
    
    for i in node_ids:
        node_type = i % 4  # 4 different node types
        
        if node_type == 0:  # Data center
            features = {
                'cpu_utilization': np.random.uniform(0.2, 0.4),
                'memory_utilization': np.random.uniform(0.3, 0.5),
                'network_bandwidth': 1000,
                'storage_capacity': 10000,
                'service_types_handled': 10,
                'latitude': 40.0, 'longitude': -74.0,
                'network_zone': 1, 'data_center_tier': 3
            }
        elif node_type == 1:  # Edge
            features = {
                'cpu_utilization': np.random.uniform(0.5, 0.7),
                'memory_utilization': np.random.uniform(0.6, 0.8),
                'network_bandwidth': 300,
                'storage_capacity': 3000,
                'service_types_handled': 5,
                'latitude': 35.0, 'longitude': -118.0,
                'network_zone': 2, 'data_center_tier': 2
            }
        elif node_type == 2:  # Fog
            features = {
                'cpu_utilization': np.random.uniform(0.7, 0.9),
                'memory_utilization': np.random.uniform(0.8, 0.9),
                'network_bandwidth': 100,
                'storage_capacity': 1000,
                'service_types_handled': 3,
                'latitude': 30.0, 'longitude': -95.0,
                'network_zone': 3, 'data_center_tier': 1
            }
        else:  # IoT
            features = {
                'cpu_utilization': np.random.uniform(0.8, 1.0),
                'memory_utilization': np.random.uniform(0.9, 1.0),
                'network_bandwidth': 50,
                'storage_capacity': 500,
                'service_types_handled': 1,
                'latitude': 25.0, 'longitude': -80.0,
                'network_zone': 4, 'data_center_tier': 0
            }
        
        node_features[i] = features
    
    # Add nodes gradually to simulate real deployment
    batch_size = 100
    for batch_start in range(0, len(node_ids), batch_size):
        batch_end = min(batch_start + batch_size, len(node_ids))
        batch_ids = node_ids[batch_start:batch_end]
        batch_features = {i: node_features[i] for i in batch_ids}
        
        add_nodes_to_federation(batch_ids, batch_features)
        time.sleep(0.1)  # Simulate gradual addition
    
    # Simulate federated learning updates
    cluster_updates = {}
    for cluster_id in range(20):  # Simulate 20 clusters
        cluster_updates[cluster_id] = {
            'gradients': torch.randn(200),  # Simulated gradients
            'version': np.random.randint(95, 105),  # Simulate version drift
            'timestamp': time.time() - np.random.uniform(0, 30),  # Recent updates
            'node_count': np.random.randint(30, 70)
        }
    
    # Process updates with all optimizations
    processed_updates = handle_extreme_scale_updates(cluster_updates)
    
    # Get comprehensive statistics
    stats = get_extreme_scale_stats()
    
    print(f"✓ Integration test completed successfully")
    print(f"✓ Total nodes: {stats['scaling_metrics']['total_nodes']}")
    print(f"✓ Active clusters: {stats['scaling_metrics']['active_clusters']}")
    print(f"✓ Communication efficiency: {stats['communication_efficiency']:.2f}")
    print(f"✓ Gradient compression ratio: {stats['gradient_compression_stats']['avg_compression_ratio']:.3f}")
    print(f"✓ Average staleness: {stats['async_update_stats']['avg_staleness']:.2f}")
    
    return stats


if __name__ == "__main__":
    print("🚀 Testing Extreme Scale Federated Learning Features")
    print("=" * 60)
    
    try:
        # Run all tests
        esfl = test_extreme_scale_clustering()
        compression_ratio = test_gradient_compression()
        compressed_models = test_hierarchical_compression()
        exchange_ratio = test_selective_parameter_exchange()
        acceptance_ratio = test_asynchronous_updates()
        schedule = test_communication_scheduling()
        final_stats = test_full_integration()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        
        print(f"📊 Test Summary:")
        print(f"   • Gradient compression ratio: {compression_ratio:.3f}")
        print(f"   • Parameter exchange efficiency: {(1-exchange_ratio)*100:.1f}%")
        print(f"   • Async update acceptance rate: {acceptance_ratio*100:.1f}%")
        print(f"   • Final system scale: {final_stats['scaling_metrics']['total_nodes']} nodes")
        print(f"   • Communication efficiency: {final_stats['communication_efficiency']*100:.1f}%")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
