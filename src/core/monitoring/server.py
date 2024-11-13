
import psutil
import torch
import time
from prometheus_client import start_http_server, Gauge
import GPUtil
from pathlib import Path
import logging

class GPUMonitor:
    def __init__(self):
        # GPU Metrics
        self.gpu_utilization = Gauge('gpu_utilization', 'GPU Utilization in %')
        self.gpu_memory_used = Gauge('gpu_memory_used', 'GPU Memory Used in MB')
        self.gpu_memory_total = Gauge('gpu_memory_total', 'GPU Total Memory in MB')
        self.gpu_temperature = Gauge('gpu_temperature', 'GPU Temperature in Celsius')
        self.gpu_power_draw = Gauge('gpu_power_draw', 'GPU Power Usage in Watts')
        
        # System Metrics
        self.cpu_usage = Gauge('cpu_usage', 'CPU Usage in %')
        self.system_memory_used = Gauge('system_memory_used', 'System Memory Used in GB')
        self.disk_usage = Gauge('disk_usage', 'Disk Usage in %')
        
        # AI Server Metrics
        self.active_tasks = Gauge('active_tasks', 'Number of Active AI Tasks')
        self.queue_size = Gauge('queue_size', 'Number of Tasks in Queue')
        self.model_loading_time = Gauge('model_loading_time', 'Time to Load Models in seconds')
        
        # Storage Metrics
        self.storage_path = Path('/data')
        self.storage_used = Gauge('storage_used', 'Storage Used in GB')
        self.storage_free = Gauge('storage_free', 'Storage Free in GB')

    def collect_metrics(self):
        """Collect all metrics."""
        try:
            # GPU Metrics
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                self.gpu_utilization.set(gpu.load * 100)
                self.gpu_memory_used.set(gpu.memoryUsed)
                self.gpu_memory_total.set(gpu.memoryTotal)
                self.gpu_temperature.set(gpu.temperature)
                if hasattr(gpu, 'powerDraw'):
                    self.gpu_power_draw.set(gpu.powerDraw)

            # System Metrics
            self.cpu_usage.set(psutil.cpu_percent())
            self.system_memory_used.set(psutil.virtual_memory().used / (1024**3))
            self.disk_usage.set(psutil.disk_usage('/').percent)

            # Storage Metrics
            if self.storage_path.exists():
                usage = psutil.disk_usage(str(self.storage_path))
                self.storage_used.set(usage.used / (1024**3))
                self.storage_free.set(usage.free / (1024**3))

        except Exception as e:
            logging.error(f"Error collecting metrics: {str(e)}")

def run_monitoring_server(port=8001):
    """Run the monitoring server."""
    start_http_server(port)
    monitor = GPUMonitor()
    
    while True:
        monitor.collect_metrics()
        time.sleep(1)  # Collect metrics every second

if __name__ == "__main__":
    run_monitoring_server()