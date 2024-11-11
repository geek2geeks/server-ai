# Location: /scripts/setup/setup_directories.py

import os
from pathlib import Path
import logging

def setup_directories():
    # Define base directory
    base_dir = Path('E:/justica')
    
    # Define directory structure
    directories = [
        'logs',
        'config/services/nginx/certs',
        'config/services/redis',
        'config/monitoring/grafana',
        'config/monitoring/prometheus',
        'src/api/v1',
        'src/core/monitoring',
        'src/core/utils',
        'data/ai',
        'data/models',
        'scripts/setup',
        'scripts/monitoring',
        'scripts/utils'
    ]
    
    # Create directories
    for dir_path in directories:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {full_path}")

if __name__ == "__main__":
    setup_directories()