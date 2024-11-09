import torch
import cv2
import numpy as np
import pandas as pd
import matplotlib
import seaborn as sns
import scipy

def test_gpu():
    print("\n=== GPU Configuration ===")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA version: {torch.version.cuda}")
        
        # Basic performance test
        size = 10000
        print(f"\nRunning performance test with {size}x{size} matrix...")
        x = torch.randn(size, size, device='cuda')
        start_time = torch.cuda.Event(enable_timing=True)
        end_time = torch.cuda.Event(enable_timing=True)
        
        start_time.record()
        result = torch.matmul(x, x)
        end_time.record()
        
        # Wait for GPU to finish
        torch.cuda.synchronize()
        
        print(f"GPU test completed successfully! Time: {start_time.elapsed_time(end_time):.2f} ms")
        
        # Memory test
        print(f"\nGPU Memory:")
        print(f"Allocated: {torch.cuda.memory_allocated(0)/1024**3:.2f} GB")
        print(f"Reserved: {torch.cuda.memory_reserved(0)/1024**3:.2f} GB")
        print(f"Max Allocated: {torch.cuda.max_memory_allocated(0)/1024**3:.2f} GB")

def test_libraries():
    print("\n=== Library Versions ===")
    print(f"OpenCV: {cv2.__version__}")
    print(f"NumPy: {np.__version__}")
    print(f"Pandas: {pd.__version__}")
    print(f"Matplotlib: {matplotlib.__version__}")
    print(f"Seaborn: {sns.__version__}")
    print(f"SciPy: {scipy.__version__}")
    
def test_gpu_capabilities():
    print("\n=== GPU Capabilities ===")
    if torch.cuda.is_available():
        device = torch.cuda.current_device()
        properties = torch.cuda.get_device_properties(device)
        
        print(f"Name: {properties.name}")
        print(f"Compute Capability: {properties.major}.{properties.minor}")
        print(f"Total Memory: {properties.total_memory/1024**3:.2f} GB")
        print(f"Multi Processors: {properties.multi_processor_count}")

def test_performance():
    print("\n=== Performance Test ===")
    if torch.cuda.is_available():
        # Test with different matrix sizes
        sizes = [1000, 5000, 10000]
        
        for size in sizes:
            print(f"\nTesting {size}x{size} matrix")
            x = torch.randn(size, size, device='cuda')
            
            start_time = torch.cuda.Event(enable_timing=True)
            end_time = torch.cuda.Event(enable_timing=True)
            
            # Warm up the GPU
            torch.matmul(x, x)
            torch.cuda.synchronize()
            
            # Actual test
            start_time.record()
            torch.matmul(x, x)
            end_time.record()
            
            torch.cuda.synchronize()
            print(f"Execution time: {start_time.elapsed_time(end_time):.2f} ms")
            print(f"Memory usage: {torch.cuda.memory_allocated(0)/1024**3:.2f} GB")

if __name__ == "__main__":
    print("=== Starting Environment Validation ===")
    test_gpu()
    test_libraries()
    test_gpu_capabilities()
    test_performance()
    print("\n=== Validation Complete ===")