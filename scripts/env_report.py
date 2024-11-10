# scripts/env_report.py

import sys
import torch
import platform
import subprocess
from pathlib import Path
import pkg_resources
import json
from datetime import datetime
import os
import psutil

def get_gpu_info():
    """Get detailed GPU information."""
    try:
        if not torch.cuda.is_available():
            return {"error": "CUDA not available"}
        
        return {
            "gpu_name": torch.cuda.get_device_name(0),
            "cuda_version": torch.version.cuda,
            "gpu_count": torch.cuda.device_count(),
            "current_device": torch.cuda.current_device(),
            "memory": {
                "allocated": f"{torch.cuda.memory_allocated(0)/1024**3:.2f}GB",
                "cached": f"{torch.cuda.memory_reserved(0)/1024**3:.2f}GB",
                "max_allocated": f"{torch.cuda.max_memory_allocated(0)/1024**3:.2f}GB"
            },
            "capabilities": {
                "compute_capability": f"{torch.cuda.get_device_capability(0)[0]}.{torch.cuda.get_device_capability(0)[1]}"
            }
        }
    except Exception as e:
        return {"error": str(e)}

def get_system_info():
    """Get system information."""
    return {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "python_path": sys.executable,
        "cpu_count": psutil.cpu_count(logical=False),
        "memory": {
            "total": f"{psutil.virtual_memory().total/1024**3:.2f}GB",
            "available": f"{psutil.virtual_memory().available/1024**3:.2f}GB",
            "used": f"{psutil.virtual_memory().used/1024**3:.2f}GB",
            "percent": f"{psutil.virtual_memory().percent}%"
        }
    }

def get_conda_info():
    """Get conda environment information."""
    try:
        conda_info = subprocess.check_output(['conda', 'info', '--json']).decode()
        return json.loads(conda_info)
    except Exception as e:
        return {"error": str(e)}

def get_installed_packages():
    """Get list of installed packages and versions."""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def generate_report():
    """Generate comprehensive environment report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_info": get_system_info(),
        "gpu_info": get_gpu_info(),
        "conda_info": get_conda_info(),
        "installed_packages": get_installed_packages(),
        "environment_variables": {k: v for k, v in os.environ.items() if 'PATH' in k or 'PYTHON' in k or 'CUDA' in k or 'CONDA' in k}
    }
    
    # Save report
    report_path = Path("docs/environment")
    report_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_path / f"env_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nEnvironment report generated: {report_file}")
    
    # Print summary
    print("\n=== Environment Summary ===")
    print(f"Python: {sys.version.split()[0]}")
    if torch.cuda.is_available():
        print(f"CUDA: {torch.version.cuda}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"PyTorch: {torch.__version__}")
    print(f"Platform: {platform.platform()}")
    print(f"CPU Cores: {psutil.cpu_count(logical=False)}")
    print(f"Memory: {psutil.virtual_memory().total/1024**3:.2f}GB")
    
    return report

if __name__ == "__main__":
    generate_report()