# src/core/metrics.py

import prometheus_client as prom
from typing import Dict
import time

class AIServerMetrics:
    def __init__(self):
        # Task Metrics
        self.active_tasks = prom.Gauge('ai_active_tasks', 'Currently running AI tasks')
        self.task_duration = prom.Histogram('ai_task_duration_seconds', 'Task processing time',
            buckets=[.1, .5, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 30.0])
        
        # Storage Metrics
        self.storage_usage = prom.Gauge('ai_storage_usage_bytes', 'Storage space used')
        self.model_cache_size = prom.Gauge('ai_model_cache_bytes', 'Model cache size')
        
        # Performance Metrics
        self.inference_time = prom.Histogram('ai_inference_seconds', 'Model inference time',
            buckets=[.01, .05, .1, .25, .5, .75, 1.0])
        
    def track_task(self, func):
        """Decorator to track task metrics"""
        def wrapper(*args, **kwargs):
            self.active_tasks.inc()
            start = time.time()
            try:
                result = func(*args, **kwargs)
                self.task_duration.observe(time.time() - start)
                return result
            finally:
                self.active_tasks.dec()
        return wrapper