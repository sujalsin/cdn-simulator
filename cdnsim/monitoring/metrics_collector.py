from prometheus_client import Counter, Gauge, Histogram, start_http_server, REGISTRY
import time
import socket
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self, port: int = 8000):
        self.port = port
        self.server_started = False
        
        # Request metrics
        self.request_counter = Counter(
            'cdn_requests_total',
            'Total number of CDN requests',
            ['node_id', 'content_type']
        )
        self.request_latency = Histogram(
            'cdn_request_latency_seconds',
            'Request latency in seconds',
            ['node_id']
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'cdn_cache_hits_total',
            'Total number of cache hits',
            ['node_id']
        )
        self.cache_misses = Counter(
            'cdn_cache_misses_total',
            'Total number of cache misses',
            ['node_id']
        )
        
        # Node metrics
        self.node_load = Gauge(
            'cdn_node_load',
            'Current load on CDN node',
            ['node_id']
        )
        self.node_capacity = Gauge(
            'cdn_node_capacity',
            'Total capacity of CDN node',
            ['node_id']
        )
        
        # ML metrics
        self.prediction_accuracy = Gauge(
            'cdn_prediction_accuracy',
            'Accuracy of traffic prediction',
            ['model_type']
        )
        self.model_training_time = Histogram(
            'cdn_model_training_seconds',
            'Time taken to train ML model'
        )

    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except socket.error:
                return True

    def find_available_port(self, start_port: int, max_attempts: int = 10) -> int:
        """Find an available port starting from start_port."""
        current_port = start_port
        for _ in range(max_attempts):
            if not self.is_port_in_use(current_port):
                return current_port
            current_port += 1
        raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

    def start_server(self):
        """Start the Prometheus metrics server."""
        if self.server_started:
            return

        try:
            # Try to find an available port
            available_port = self.find_available_port(self.port)
            if available_port != self.port:
                logger.info(f"Port {self.port} is in use, using port {available_port} instead")
                self.port = available_port

            start_http_server(self.port)
            self.server_started = True
            logger.info(f"Metrics server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
            raise

    def record_request(self, node_id: str, content_type: str, latency: float):
        """Record a content request."""
        try:
            self.request_counter.labels(node_id=node_id, content_type=content_type).inc()
            self.request_latency.labels(node_id=node_id).observe(latency)
        except Exception as e:
            logger.error(f"Error recording request metrics: {e}")

    def update_cache_metrics(self, node_id: str, hit: bool):
        """Update cache hit/miss metrics."""
        try:
            if hit:
                self.cache_hits.labels(node_id=node_id).inc()
            else:
                self.cache_misses.labels(node_id=node_id).inc()
        except Exception as e:
            logger.error(f"Error updating cache metrics: {e}")

    def update_node_metrics(self, node_id: str, load: float, capacity: float):
        """Update node load and capacity metrics."""
        try:
            self.node_load.labels(node_id=node_id).set(load)
            self.node_capacity.labels(node_id=node_id).set(capacity)
        except Exception as e:
            logger.error(f"Error updating node metrics: {e}")

    def record_prediction_accuracy(self, model_type: str, accuracy: float):
        """Record ML model prediction accuracy."""
        try:
            self.prediction_accuracy.labels(model_type=model_type).set(accuracy)
        except Exception as e:
            logger.error(f"Error recording prediction accuracy: {e}")

    def record_model_training(self, duration: float):
        """Record ML model training duration."""
        try:
            self.model_training_time.observe(duration)
        except Exception as e:
            logger.error(f"Error recording model training time: {e}")

    def get_current_metrics(self) -> Dict:
        """Get current metrics for monitoring dashboard."""
        try:
            # Get all metrics from the registry
            metrics = {}
            
            # Calculate total requests
            total_requests = 0
            for metric in REGISTRY.collect():
                if metric.name == 'cdn_requests_total':
                    for sample in metric.samples:
                        total_requests += sample.value

            # Calculate average latency
            latency_sum = 0
            latency_count = 0
            for metric in REGISTRY.collect():
                if metric.name == 'cdn_request_latency_seconds_sum':
                    for sample in metric.samples:
                        latency_sum += sample.value
                elif metric.name == 'cdn_request_latency_seconds_count':
                    for sample in metric.samples:
                        latency_count += sample.value

            # Calculate cache hit rate
            cache_hits = 0
            cache_misses = 0
            for metric in REGISTRY.collect():
                if metric.name == 'cdn_cache_hits_total':
                    for sample in metric.samples:
                        cache_hits += sample.value
                elif metric.name == 'cdn_cache_misses_total':
                    for sample in metric.samples:
                        cache_misses += sample.value

            # Get prediction accuracy
            prediction_accuracy = 0
            for metric in REGISTRY.collect():
                if metric.name == 'cdn_prediction_accuracy':
                    for sample in metric.samples:
                        prediction_accuracy = sample.value
                        break

            metrics['total_requests'] = total_requests
            metrics['average_latency'] = latency_sum / max(latency_count, 1)
            metrics['cache_hit_rate'] = cache_hits / max(cache_hits + cache_misses, 1)
            metrics['prediction_accuracy'] = prediction_accuracy

            return metrics
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {}
