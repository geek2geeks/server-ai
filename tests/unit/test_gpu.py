import pytest
import torch

def test_gpu_availability():
    assert torch.cuda.is_available(), "GPU not available"
    assert torch.cuda.device_count() > 0, "No GPU devices found"
    assert torch.cuda.current_device() >= 0, "No current GPU device"

def test_gpu_memory():
    if torch.cuda.is_available():
        properties = torch.cuda.get_device_properties(0)
        assert properties.total_memory > 20 * 1024 * 1024 * 1024, "Less than 20GB GPU memory"
        
def test_cuda_version():
    if torch.cuda.is_available():
        assert torch.__version__ >= "2.5.1", "PyTorch version too old"
        assert torch.version.cuda >= "12.1", "CUDA version too old"

def test_gpu_compute_capability():
    if torch.cuda.is_available():
        properties = torch.cuda.get_device_properties(0)
        assert properties.major >= 8, "GPU compute capability too low"