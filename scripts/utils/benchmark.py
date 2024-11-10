# scripts/gpu_benchmark.py

import torch
import time
import json
from pathlib import Path
from datetime import datetime
import numpy as np

def run_gpu_benchmarks():
    """Run comprehensive GPU benchmarks."""
    if not torch.cuda.is_available():
        return {"error": "CUDA not available"}
    
    results = {}
    
    # Memory transfer tests
    sizes = [(1000, 1000), (5000, 5000), (10000, 10000)]
    for size in sizes:
        # CPU to GPU transfer
        x = torch.randn(size)
        start = time.perf_counter()
        x_gpu = x.cuda()
        torch.cuda.synchronize()
        cpu_to_gpu = time.perf_counter() - start
        
        # GPU to CPU transfer
        start = time.perf_counter()
        x_cpu = x_gpu.cpu()
        torch.cuda.synchronize()
        gpu_to_cpu = time.perf_counter() - start
        
        results[f"transfer_{size[0]}x{size[1]}"] = {
            "cpu_to_gpu_ms": cpu_to_gpu * 1000,
            "gpu_to_cpu_ms": gpu_to_cpu * 1000,
            "matrix_size_mb": np.prod(size) * 4 / (1024 * 1024)
        }
        
        del x_gpu, x_cpu
    
    # Computation tests
    for size in sizes:
        # Matrix multiplication
        a = torch.randn(size).cuda()
        b = torch.randn(size).cuda()
        
        # Warmup
        torch.matmul(a, b)
        torch.cuda.synchronize()
        
        # Timed run
        start = time.perf_counter()
        for _ in range(10):
            c = torch.matmul(a, b)
            torch.cuda.synchronize()
        compute_time = (time.perf_counter() - start) / 10
        
        results[f"matmul_{size[0]}x{size[1]}"] = {
            "compute_time_ms": compute_time * 1000,
            "tflops": (2 * np.prod(size) * size[0]) / (compute_time * 1e12)
        }
        
        del a, b, c
    
    # Memory bandwidth test
    size = 1024 * 1024 * 128  # 512MB
    x = torch.randn(size).cuda()
    start = time.perf_counter()
    for _ in range(10):
        y = x * 2 + 1
        torch.cuda.synchronize()
    bandwidth_time = (time.perf_counter() - start) / 10
    
    results["memory_bandwidth"] = {
        "size_gb": size * 4 / (1024**3),
        "bandwidth_gbps": (size * 4 * 3) / (bandwidth_time * 1024**3)
    }
    
    # Save results
    benchmark_path = Path("docs/benchmarks")
    benchmark_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    benchmark_file = benchmark_path / f"gpu_benchmark_{timestamp}.json"
    
    with open(benchmark_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nBenchmark results saved to: {benchmark_file}")
    return results

if __name__ == "__main__":
    results = run_gpu_benchmarks()
    print("\n=== GPU Benchmark Results ===")
    print(json.dumps(results, indent=2))