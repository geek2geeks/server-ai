# scripts/docker_test.py

import torch
import sys
import GPUtil
import numpy as np
from pathlib import Path

def run_docker_test():
    print("\n=== Docker Container GPU Test ===\n")
    
    # System info
    print(f"Python version: {sys.version}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU device: {torch.cuda.get_device_name(0)}")
        
        # GPU info
        gpu = GPUtil.getGPUs()[0]
        print(f"\nGPU Memory Total: {gpu.memoryTotal}MB")
        print(f"GPU Memory Free: {gpu.memoryFree}MB")
        print(f"GPU Temperature: {gpu.temperature}°C")
        
        # Run a simple GPU operation
        print("\nRunning GPU performance test...")
        
        # Matrix multiplication test
        size = 5000
        a = torch.randn(size, size, device='cuda')
        b = torch.randn(size, size, device='cuda')
        
        # CUDA events for timing
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        
        # Warmup
        torch.matmul(a, b)
        torch.cuda.synchronize()
        
        # Timed run
        start.record()
        c = torch.matmul(a, b)
        end.record()
        torch.cuda.synchronize()
        
        print(f"Matrix multiplication ({size}x{size}): {start.elapsed_time(end):.2f}ms")
        
        # Memory cleanup
        del a, b, c
        torch.cuda.empty_cache()
        
        print("\nGPU test completed successfully!")
    else:
        print("No CUDA GPU available in container!")
        sys.exit(1)

if __name__ == "__main__":
    run_docker_test()