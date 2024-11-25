import logging
import random
from typing import Dict, List, Optional, Tuple
import time
import numpy as np

from ..monitoring.metrics_collector import MetricsCollector
from ..ml.traffic_predictor import TrafficPredictor
from ..caching.cache_manager import CacheManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CDNNode:
    def __init__(self, node_id: str, location: str, capacity: float):
        self.node_id = node_id
        self.location = location
        self.capacity = capacity
        self.current_load = 0
        self.performance_metrics = {
            'requests_handled': 0,
            'avg_latency': 0,
            'total_latency': 0
        }

    def handle_request(self, content_type: str) -> Tuple[bool, float]:
        """Handle a content request and return success status and latency."""
        if self.current_load >= self.capacity:
            return False, 0.0

        # Simulate request processing
        latency = random.uniform(0.1, 2.0)  # Simulated latency between 100ms and 2s
        self.current_load += 1
        
        # Update metrics
        self.performance_metrics['requests_handled'] += 1
        self.performance_metrics['total_latency'] += latency
        self.performance_metrics['avg_latency'] = (
            self.performance_metrics['total_latency'] / 
            self.performance_metrics['requests_handled']
        )
        
        return True, latency

class CDNSimulator:
    def __init__(self, num_nodes: int = 5, metrics_port: int = 8000):
        self.nodes: Dict[str, CDNNode] = {}
        self.metrics = MetricsCollector(port=metrics_port)
        self.predictor = TrafficPredictor()
        self.cache_manager = CacheManager()
        
        # Initialize nodes with random capacities
        locations = ['US', 'Europe', 'Asia', 'Australia', 'South America']
        for i in range(num_nodes):
            node_id = f'node_{i}'
            location = locations[i % len(locations)]
            capacity = random.uniform(100, 200)  # Random capacity between 100-200
            self.nodes[node_id] = CDNNode(node_id, location, capacity)
            logger.info(f"Initialized {node_id} in {location} with capacity {capacity:.2f}")

        try:
            self.metrics.start_server()
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
            logger.warning("Continuing without metrics collection")

    def select_node(self, content_type: str) -> Optional[CDNNode]:
        """Select the best node to handle a request based on load percentage."""
        available_nodes = [
            node for node in self.nodes.values()
            if node.current_load < node.capacity
        ]
        
        if not available_nodes:
            return None
            
        # Select node with lowest load percentage
        return min(
            available_nodes,
            key=lambda n: (n.current_load / n.capacity)
        )

    def handle_request(self, content_type: str) -> bool:
        """Handle an incoming content request."""
        node = self.select_node(content_type)
        if not node:
            logger.warning("No available nodes to handle request")
            return False

        # Check cache first
        cache_hit = self.cache_manager.get(content_type) is not None
        
        # Process request
        success, latency = node.handle_request(content_type)
        
        if success:
            # Record metrics
            try:
                self.metrics.record_request(node.node_id, content_type, latency)
                self.metrics.update_cache_metrics(node.node_id, cache_hit)
                self.metrics.update_node_metrics(
                    node.node_id,
                    node.current_load,
                    node.capacity
                )
            except Exception as e:
                logger.error(f"Failed to record metrics: {e}")
            
            # Update cache
            if not cache_hit:
                self.cache_manager.set(content_type, f"content_data_{content_type}")
        
        return success

    def get_node_metrics(self) -> Dict:
        """Get current performance metrics for all nodes."""
        return {
            node_id: node.performance_metrics
            for node_id, node in self.nodes.items()
        }

    def train_predictor(self, historical_data: Optional[List[Dict]] = None):
        """Train the traffic predictor with historical data."""
        start_time = time.time()
        
        if historical_data is None:
            # Use synthetic data
            hour = time.localtime().tm_hour
            day = time.localtime().tm_wday
            
            # Create synthetic data point
            features = [hour, day, 0, 0]  # Using current hour and day
            historical_data = {
                'features': np.array([features]),
                'target': np.array([100.0])  # Default target value
            }
        
        self.predictor.train(historical_data)
        training_time = time.time() - start_time
        
        try:
            self.metrics.record_model_training(training_time)
            self.metrics.record_prediction_accuracy(
                "random_forest",
                self.predictor.get_accuracy()
            )
        except Exception as e:
            logger.error(f"Failed to record training metrics: {e}")

    def get_current_metrics(self) -> Dict:
        """Get current system-wide metrics."""
        try:
            return self.metrics.get_current_metrics()
        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
            return {}

class CacheManager:
    def __init__(self):
        self.cache = {}

    def get(self, content_id: str) -> Optional[str]:
        """Get content from cache."""
        return self.cache.get(content_id)

    def set(self, content_id: str, content_data: str):
        """Set content in cache."""
        self.cache[content_id] = content_data
