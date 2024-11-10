# scripts/test_cv_gpu.py

import torch
import cv2
import numpy as np
import time
from pathlib import Path

def test_cv_gpu_capabilities():
    print("\n=== Testing CV and GPU Capabilities ===\n")
    
    # 1. Test GPU Availability
    print("GPU Configuration:")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    # 2. Test OpenCV
    print("\nOpenCV Configuration:")
    print(f"OpenCV Version: {cv2.__version__}")
    
    # 3. Create test image and perform GPU operations
    print("\nPerforming CV Operations:")
    
    # Create synthetic image
    image_size = (3840, 2160)  # 4K resolution
    print(f"Creating {image_size[0]}x{image_size[1]} test image...")
    
    # Create a gradient image
    x = np.linspace(0, 1, image_size[1])
    y = np.linspace(0, 1, image_size[0])
    xx, yy = np.meshgrid(x, y)
    test_image = (xx + yy) * 255
    test_image = test_image.astype(np.uint8)
    
    # Convert to GPU tensor
    start_time = time.time()
    gpu_tensor = torch.from_numpy(test_image).cuda().float()
    print(f"GPU Transfer Time: {(time.time() - start_time)*1000:.2f}ms")
    
    # Perform GPU operations
    print("\nPerforming GPU Operations:")
    
    # 1. Convolution test
    start_time = time.time()
    kernel = torch.ones(5, 5).cuda() / 25
    kernel = kernel.view(1, 1, 5, 5)
    gpu_tensor = gpu_tensor.view(1, 1, *image_size)
    conv_result = torch.nn.functional.conv2d(gpu_tensor, kernel, padding=2)
    torch.cuda.synchronize()
    print(f"4K Image Convolution Time: {(time.time() - start_time)*1000:.2f}ms")
    
    # 2. Multiple transformations
    start_time = time.time()
    for _ in range(10):
        # Simulate complex image processing
        transformed = torch.nn.functional.interpolate(gpu_tensor, scale_factor=0.5)
        transformed = torch.nn.functional.interpolate(transformed, size=image_size)
    torch.cuda.synchronize()
    print(f"10x Resolution Transform Time: {(time.time() - start_time)*1000:.2f}ms")
    
    # Memory cleanup
    del gpu_tensor, conv_result, transformed
    torch.cuda.empty_cache()
    
    print("\nGPU Memory After Cleanup:")
    print(f"Allocated: {torch.cuda.memory_allocated()/1e9:.2f} GB")
    print(f"Reserved: {torch.cuda.memory_reserved()/1e9:.2f} GB")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    try:
        test_cv_gpu_capabilities()
    except Exception as e:
        print(f"Test failed: {str(e)}")