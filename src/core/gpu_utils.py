import torch
from typing import Dict, Any

class GPUManager:
    @staticmethod
    def get_gpu_info() -> Dict[str, Any]:
        """
        Get current GPU information and status
        """
        if not torch.cuda.is_available():
            return {"status": "GPU not available"}
            
        gpu_info = {
            "gpu_name": torch.cuda.get_device_name(0),
            "compute_capability": f"{torch.cuda.get_device_properties(0).major}.{torch.cuda.get_device_properties(0).minor}",
            "gpu_memory_total": f"{torch.cuda.get_device_properties(0).total_memory/1024**3:.2f}GB",
            "gpu_memory_allocated": f"{torch.cuda.memory_allocated(0)/1024**3:.2f}GB",
            "gpu_memory_reserved": f"{torch.cuda.memory_reserved(0)/1024**3:.2f}GB",
            "cuda_version": torch.version.cuda,
            "pytorch_version": torch.__version__
        }
        return gpu_info

    @staticmethod
    def clear_gpu_memory() -> Dict[str, str]:
        """
        Clear GPU memory cache
        """
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.memory.empty_cache()
            return {"status": "GPU memory cleared"}
        return {"status": "GPU not available"}

    @staticmethod
    def get_memory_status() -> Dict[str, float]:
        """
        Get detailed memory status
        """
        if not torch.cuda.is_available():
            return {"error": "GPU not available"}
            
        return {
            "total_memory": torch.cuda.get_device_properties(0).total_memory/1024**3,
            "allocated_memory": torch.cuda.memory_allocated(0)/1024**3,
            "reserved_memory": torch.cuda.memory_reserved(0)/1024**3,
            "max_memory_allocated": torch.cuda.max_memory_allocated(0)/1024**3
        }