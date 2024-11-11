# Location: E:/justica/scripts/services/validate_services.py

import os
import sys
import logging
import requests
import docker
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceValidator:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.containers = {
            'justica_ai_server': 8000,
            'justica_grafana': 3000,
            'justica_prometheus': 9090,
            'justica_redis': 6379,
            'justica_nginx': 80
        }

    def check_docker_services(self):
        """Check if all required Docker services are running"""
        try:
            containers = self.docker_client.containers.list()
            running_containers = {c.name: c for c in containers}
            
            logger.info("Checking Docker services...")
            for container_name in self.containers.keys():
                if container_name not in running_containers:
                    logger.error(f"Container {container_name} is not running")
                    continue
                
                container = running_containers[container_name]
                status = container.status
                logger.info(f"✓ Container {container_name} is {status}")
                
                # Log container logs if not running properly
                if status != 'running':
                    logs = container.logs(tail=50).decode()
                    logger.error(f"Container logs:\n{logs}")
                    
            return True
        except Exception as e:
            logger.error(f"Error checking Docker services: {e}")
            return False

    def check_service_health(self):
        """Check if services are responding"""
        endpoints = {
            'AI Server': 'http://localhost:8000/health',
            'Grafana': 'http://localhost:3000/api/health',
            'Prometheus': 'http://localhost:9090/-/healthy'
        }

        logger.info("Checking service health...")
        for service, url in endpoints.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    logger.info(f"✓ {service} is healthy")
                else:
                    logger.error(f"✗ {service} returned status code {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"✗ Cannot connect to {service}: {e}")

    def check_gpu_availability(self):
        """Check if GPU is available in AI server container"""
        try:
            container = self.docker_client.containers.get('justica_ai_server')
            result = container.exec_run('python3 -c "import torch; print(torch.cuda.is_available())"')
            if 'True' in result.output.decode():
                logger.info("✓ GPU is available in AI server")
                return True
            else:
                logger.error("✗ GPU is not available in AI server")
                return False
        except Exception as e:
            logger.error(f"Error checking GPU availability: {e}")
            return False

def main():
    logger.info("Starting service validation...")
    validator = ServiceValidator()

    # Check Docker services
    if not validator.check_docker_services():
        logger.error("Docker services check failed")
        return

    # Wait for services to fully start
    logger.info("Waiting for services to initialize...")
    time.sleep(10)

    # Check service health
    validator.check_service_health()

    # Check GPU availability
    validator.check_gpu_availability()

if __name__ == "__main__":
    main()