# scripts/monitoring/validate.py

import sys
import os
import torch
import cv2
import numpy as np
import pandas as pd
import matplotlib
import seaborn as sns
import scipy
import logging
import psutil
import GPUtil
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemValidator:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "status": "initializing",
            "tests": {}
        }

    def test_gpu(self):
        """Test GPU configuration and performance."""
        logger.info("Testing GPU configuration...")
        try:
            gpu_info = {
                "pytorch_version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            }

            if torch.cuda.is_available():
                gpu_info.update({
                    "gpu_name": torch.cuda.get_device_name(0),
                    "gpu_count": torch.cuda.device_count(),
                    "memory": {
                        "allocated": f"{torch.cuda.memory_allocated()/1024**3:.2f}GB",
                        "reserved": f"{torch.cuda.memory_reserved()/1024**3:.2f}GB",
                        "max_allocated": f"{torch.cuda.max_memory_allocated()/1024**3:.2f}GB"
                    }
                })

                # Performance test
                size = 10000
                x = torch.randn(size, size, device='cuda')
                start_time = torch.cuda.Event(enable_timing=True)
                end_time = torch.cuda.Event(enable_timing=True)
                
                start_time.record()
                result = torch.matmul(x, x)
                end_time.record()
                torch.cuda.synchronize()
                
                gpu_info["performance_test"] = {
                    "matrix_size": f"{size}x{size}",
                    "computation_time": f"{start_time.elapsed_time(end_time):.2f}ms"
                }

            self.results["tests"]["gpu"] = {
                "status": "passed",
                "info": gpu_info
            }
        except Exception as e:
            logger.error(f"GPU test failed: {str(e)}")
            self.results["tests"]["gpu"] = {
                "status": "failed",
                "error": str(e)
            }

    def test_libraries(self):
        """Test required library versions."""
        logger.info("Testing library versions...")
        try:
            libraries = {
                "opencv": cv2.__version__,
                "numpy": np.__version__,
                "pandas": pd.__version__,
                "matplotlib": matplotlib.__version__,
                "seaborn": sns.__version__,
                "scipy": scipy.__version__
            }
            
            self.results["tests"]["libraries"] = {
                "status": "passed",
                "versions": libraries
            }
        except Exception as e:
            logger.error(f"Library test failed: {str(e)}")
            self.results["tests"]["libraries"] = {
                "status": "failed",
                "error": str(e)
            }

    def test_directories(self):
        """Validate project directory structure."""
        logger.info("Validating directory structure...")
        required_dirs = [
            "config/monitoring/grafana",
            "config/monitoring/prometheus",
            "config/services/cloudflare",
            "config/services/redis",
            "scripts/monitoring",
            "scripts/utils",
            "src/api/v1",
            "src/core/monitoring",
            "src/core/utils",
            "data/ai",
            "data/models"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = Path(dir_path)
            if not full_path.exists():
                missing_dirs.append(dir_path)
                
        self.results["tests"]["directories"] = {
            "status": "passed" if not missing_dirs else "failed",
            "missing_directories": missing_dirs
        }

    def test_system_resources(self):
        """Check system resources."""
        logger.info("Checking system resources...")
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            resources = {
                "cpu": {
                    "cores": psutil.cpu_count(logical=False),
                    "threads": psutil.cpu_count(logical=True),
                    "usage": f"{psutil.cpu_percent()}%"
                },
                "memory": {
                    "total": f"{memory.total/1024**3:.1f}GB",
                    "available": f"{memory.available/1024**3:.1f}GB",
                    "percent": f"{memory.percent}%"
                },
                "disk": {
                    "total": f"{disk.total/1024**3:.1f}GB",
                    "free": f"{disk.free/1024**3:.1f}GB",
                    "percent": f"{disk.percent}%"
                }
            }
            
            self.results["tests"]["resources"] = {
                "status": "passed",
                "info": resources
            }
        except Exception as e:
            logger.error(f"Resource check failed: {str(e)}")
            self.results["tests"]["resources"] = {
                "status": "failed",
                "error": str(e)
            }

    def run_all_tests(self):
        """Run all validation tests."""
        logger.info("Starting system validation...")
        try:
            self.test_gpu()
            self.test_libraries()
            self.test_directories()
            self.test_system_resources()
            
            # Set overall status
            all_passed = all(test["status"] == "passed" for test in self.results["tests"].values())
            self.results["status"] = "passed" if all_passed else "failed"
            
            # Save results
            self.save_results()
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            self.results["status"] = "error"
            self.results["error"] = str(e)

    def save_results(self):
        """Save validation results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("docs/validation")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"validation_{timestamp}.json"
        import json
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        logger.info(f"Validation results saved to: {output_file}")

def main():
    validator = SystemValidator()
    validator.run_all_tests()
    
    # Print summary
    print("\n=== Validation Summary ===")
    print(f"Status: {validator.results['status']}")
    for test_name, test_results in validator.results["tests"].items():
        print(f"\n{test_name.upper()}: {test_results['status']}")
        if test_results["status"] == "failed" and "error" in test_results:
            print(f"Error: {test_results['error']}")

if __name__ == "__main__":
    main()