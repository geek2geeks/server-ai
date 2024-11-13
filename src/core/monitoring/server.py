import psutil
import torch
import time
from prometheus_client import start_http_server, Gauge, Counter
import GPUtil
from pathlib import Path
import logging

class GPUMonitor:
    def __init__(self):
        # GPU Core Metrics
        self.gpu_utilization = Gauge('gpu_utilization', 'GPU Utilization in %')
        self.gpu_memory_used = Gauge('gpu_memory_used_mb', 'GPU Memory Used in MB')
        self.gpu_memory_total = Gauge('gpu_memory_total_mb', 'GPU Total Memory in MB')
        self.gpu_temperature = Gauge('gpu_temperature_celsius', 'GPU Temperature in Celsius')
        self.gpu_power_draw = Gauge('gpu_power_watts', 'GPU Power Usage in Watts')
        
        # GPU Performance Metrics
        self.gpu_memory_bandwidth = Gauge('gpu_memory_bandwidth_gbps', 'GPU Memory Bandwidth in GB/s')
        self.gpu_pcie_throughput = Gauge('gpu_pcie_throughput_gbps', 'GPU PCIe Throughput in GB/s')
        self.gpu_compute_mode = Gauge('gpu_compute_mode', 'GPU Compute Mode')
        
        # System Metrics
        self.cpu_usage = Gauge('cpu_usage_percent', 'CPU Usage in %')
        self.system_memory_used = Gauge('system_memory_gb', 'System Memory Used in GB')
        self.disk_usage = Gauge('disk_usage_percent', 'Disk Usage in %')
        
        # AI Server Metrics
        self.active_tasks = Gauge('ai_active_tasks', 'Number of Active AI Tasks')
        self.queue_size = Gauge('ai_queue_size', 'Number of Tasks in Queue')
        self.model_loading_time = Gauge('ai_model_loading_seconds', 'Time to Load Models in seconds')
        
        # Operation Counters
        self.gpu_operations = Counter('gpu_operations_total', 'Total GPU Operations')
        self.memory_allocation_errors = Counter('gpu_memory_errors_total', 'GPU Memory Allocation Errors')
        self.cuda_errors = Counter('gpu_cuda_errors_total', 'CUDA Errors')
        
        # Performance Metrics
        self.inference_latency = Gauge('ai_inference_latency_ms', 'Model Inference Latency in ms')
        self.batch_processing_time = Gauge('ai_batch_processing_ms', 'Batch Processing Time in ms')
        
        # Storage Metrics
        self.storage_path = Path('/data')
        self.storage_used = Gauge('storage_used_gb', 'Storage Used in GB')
        self.storage_free = Gauge('storage_free_gb', 'Storage Free in GB')

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

            # Additional GPU Metrics (if available)
            if torch.cuda.is_available():
                device = torch.cuda.current_device()
                self.gpu_compute_mode.set(torch.cuda.get_device_capability(device)[0])
                # Update operation counter
                self.gpu_operations.inc()

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
            self.cuda_errors.inc()

    def run_latency_test(self):
        """Run a simple operation to measure GPU latency."""
        try:
            if torch.cuda.is_available():
                start = torch.cuda.Event(enable_timing=True)
                end = torch.cuda.Event(enable_timing=True)
                
                x = torch.randn(1000, 1000, device='cuda')
                
                start.record()
                torch.matmul(x, x)
                end.record()
                
                torch.cuda.synchronize()
                self.inference_latency.set(start.elapsed_time(end))
        except Exception:
            self.cuda_errors.inc()

def run_monitoring_server(port=8001):
    """Run the monitoring server."""
    start_http_server(port)
    monitor = GPUMonitor()
    logging.info(f"Metrics server started on port {port}")
    
    while True:
        monitor.collect_metrics()
        monitor.run_latency_test()
        time.sleep(1)

if __name__ == "__main__":
    run_monitoring_server()