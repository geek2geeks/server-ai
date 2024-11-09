# src/core/gpu_utils.py

import torch
import logging
from typing import Dict, Optional, List
import psutil
import GPUtil
from dataclasses import dataclass

@dataclass
class GPUStats:
    """Data class for GPU statistics"""
    id: int
    load: float  # GPU utilization %
    memory_total: int  # Total memory in MB
    memory_used: int  # Used memory in MB
    memory_free: int  # Free memory in MB
    temperature: float  # Temperature in Celsius
    power_draw: float  # Power usage in Watts

class GPUManager:
    """
    Manages GPU resources and provides utilities for monitoring and allocation.
    This is a core component used by the distributed server to manage GPU workloads
    across different AI tasks (RAG, video translation, etc.).
    """
    def __init__(self, log_level: int = logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        if not torch.cuda.is_available():
            raise RuntimeError("No CUDA-capable GPU detected")
        
        self.device_count = torch.cuda.device_count()
        self.logger.info(f"Initialized GPUManager with {self.device_count} devices")

    def get_gpu_stats(self, device_id: Optional[int] = None) -> Dict[int, GPUStats]:
        """
        Get current statistics for all GPUs or a specific GPU.
        
        Args:
            device_id: Optional specific GPU ID to query
            
        Returns:
            Dictionary mapping GPU IDs to their statistics
        """
        gpus = GPUtil.getGPUs()
        stats = {}
        
        for gpu in gpus:
            if device_id is not None and gpu.id != device_id:
                continue
                
            stats[gpu.id] = GPUStats(
                id=gpu.id,
                load=gpu.load * 100,
                memory_total=gpu.memoryTotal,
                memory_used=gpu.memoryUsed,
                memory_free=gpu.memoryFree,
                temperature=gpu.temperature,
                power_draw=gpu.powerDraw if hasattr(gpu, 'powerDraw') else 0.0
            )
            
        return stats

    def allocate_optimal_device(self, required_memory_mb: int = 0) -> int:
        """
        Allocates the most suitable GPU for a given task based on current load and memory.
        
        Args:
            required_memory_mb: Minimum required GPU memory in MB
            
        Returns:
            ID of the optimal GPU device
            
        Raises:
            RuntimeError: If no GPU with sufficient memory is available
        """
        stats = self.get_gpu_stats()
        best_device = None
        best_score = float('inf')
        
        for device_id, gpu_stat in stats.items():
            if gpu_stat.memory_free < required_memory_mb:
                continue
                
            # Score based on load and available memory
            score = (gpu_stat.load * 0.7) + ((gpu_stat.memory_used / gpu_stat.memory_total) * 0.3)
            
            if score < best_score:
                best_score = score
                best_device = device_id
                
        if best_device is None:
            raise RuntimeError(f"No GPU with required memory ({required_memory_mb}MB) available")
            
        return best_device

    def get_system_memory_usage(self) -> Dict[str, float]:
        """
        Get system memory statistics.
        
        Returns:
            Dictionary containing system memory usage information
        """
        memory = psutil.virtual_memory()
        return {
            "total_gb": memory.total / (1024**3),
            "used_gb": memory.used / (1024**3),
            "free_gb": memory.available / (1024**3),
            "percent_used": memory.percent
        }

    def cleanup_gpu_memory(self, device_id: Optional[int] = None):
        """
        Cleanup CUDA memory for specific or all devices.
        
        Args:
            device_id: Optional specific GPU ID to clean
        """
        if device_id is not None:
            torch.cuda.empty_cache()
            return
            
        for dev_id in range(self.device_count):
            with torch.cuda.device(dev_id):
                torch.cuda.empty_cache()
                
        self.logger.info("GPU memory cleaned up")