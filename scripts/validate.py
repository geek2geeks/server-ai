# Location: E:/justica/scripts/validate.py

import os
import sys
import torch
import cv2
import numpy as np
import pandas as pd
import logging
import psutil
import docker
import json
import redis
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedValidator:
    """
    Unified system validator that combines GPU, services, config, and directory validation.
    """
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "status": "initializing",
            "tests": {}
        }
        self.docker_client = docker.from_env()
        
        # Load environment variables
        load_dotenv()

    def validate_all(self):
        """Run all validation checks."""
        try:
            self.validate_environment()
            self.validate_gpu()
            self.validate_services()
            self.validate_directories()
            self.validate_redis()
            self.validate_system_resources()
            
            # Set overall status
            all_passed = all(test["status"] == "passed" for test in self.results["tests"].values())
            self.results["status"] = "passed" if all_passed else "failed"
            
            # Save results
            self.save_results()
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            self.results["status"] = "error"
            self.results["error"] = str(e)

    def validate_environment(self):
        """Validate environment variables."""
        required_vars = [
            'CLOUDFLARE_TOKEN',
            'API_SECRET_KEY',
            'REDIS_PASSWORD',
            'POSTGRES_PASSWORD',
            'GRAFANA_ADMIN_PASSWORD'
        ]
        
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        self.results["tests"]["environment"] = {
            "status": "passed" if not missing else "failed",
            "missing_variables": missing
        }

    def validate_gpu(self):
        """Validate GPU configuration and performance."""
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
            logger.error(f"GPU validation failed: {str(e)}")
            self.results["tests"]["gpu"] = {
                "status": "failed",
                "error": str(e)
            }

    def validate_services(self):
        """Validate Docker services."""
        try:
            required_services = {
                'justica_ai_server': 8000,
                'justica_grafana': 3000,
                'justica_prometheus': 9090,
                'justica_redis': 6379,
                'justica_nginx': 80
            }
            
            containers = self.docker_client.containers.list()
            running_containers = {c.name: c for c in containers}
            
            service_status = {}
            for service_name, port in required_services.items():
                if service_name in running_containers:
                    container = running_containers[service_name]
                    service_status[service_name] = {
                        "status": container.status,
                        "port": port
                    }
                else:
                    service_status[service_name] = {
                        "status": "not_found",
                        "port": port
                    }
            
            self.results["tests"]["services"] = {
                "status": "passed" if all(s["status"] == "running" for s in service_status.values()) else "failed",
                "services": service_status
            }
        except Exception as e:
            logger.error(f"Service validation failed: {str(e)}")
            self.results["tests"]["services"] = {
                "status": "failed",
                "error": str(e)
            }

    def validate_directories(self):
        """Validate project directory structure."""
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

    def validate_redis(self):
        """Validate Redis connection."""
        try:
            r = redis.Redis(
                host='localhost',
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD'),
                ssl=os.getenv('REDIS_TLS_ENABLED', 'true').lower() == 'true'
            )
            r.ping()
            
            self.results["tests"]["redis"] = {
                "status": "passed",
                "info": {
                    "connected": True,
                    "port": os.getenv('REDIS_PORT', 6379)
                }
            }
        except Exception as e:
            logger.error(f"Redis validation failed: {str(e)}")
            self.results["tests"]["redis"] = {
                "status": "failed",
                "error": str(e)
            }

    def validate_system_resources(self):
        """Validate system resources."""
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
            logger.error(f"Resource validation failed: {str(e)}")
            self.results["tests"]["resources"] = {
                "status": "failed",
                "error": str(e)
            }

    def save_results(self):
        """Save validation results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("docs/validation")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"validation_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        logger.info(f"Validation results saved to: {output_file}")

def main():
    """Main execution function."""
    validator = UnifiedValidator()
    validator.validate_all()
    
    # Print summary
    print("\n=== Validation Summary ===")
    print(f"Status: {validator.results['status']}")
    for test_name, test_results in validator.results["tests"].items():
        print(f"\n{test_name.upper()}: {test_results['status']}")
        if test_results["status"] == "failed" and "error" in test_results:
            print(f"Error: {test_results['error']}")

if __name__ == "__main__":
    main()