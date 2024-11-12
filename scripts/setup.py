# Location: E:/justica/scripts/setup.py

import os
import sys
import shutil
import ctypes
import secrets
import string
import logging
import json
import subprocess
import socket
import time
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemSetup:
    """
    Unified system setup handling directories, SSL, authentication, and secrets.
    """
    def __init__(self):
        self.base_dir = Path('E:/justica')
        self.certbot_path = Path(r"C:\Program Files\Certbot\bin\certbot.exe")
        self.required_dirs = [
            'logs',
            'config/services/nginx/certs',
            'config/services/nginx',
            'config/services/redis',
            'config/monitoring/grafana',
            'config/monitoring/prometheus',
            'src/api/v1',
            'src/core/monitoring',
            'src/core/utils',
            'data/ai',
            'data/models',
            'scripts',
            'docs/validation'
        ]

    def setup_all(self):
        """Run all setup procedures."""
        try:
            self.check_admin()
            self.setup_directories()
            
            ssl_success = self.setup_ssl(retries=3)
            if not ssl_success:
                logger.warning("SSL setup incomplete - continuing with other steps")
                
            self.setup_auth()
            self.generate_secrets()
            
            logger.info("System setup completed!")
            if not ssl_success:
                logger.warning("\nNOTE: SSL certificates were not set up.")
                logger.warning("You can run setup again later to complete SSL setup.")
                
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            sys.exit(1)

    def check_admin(self):
        """Check for administrative privileges."""
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                logger.error("This script requires administrative privileges.")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Admin check failed: {e}")
            sys.exit(1)

    def setup_directories(self):
        """Create required directories."""
        try:
            for dir_path in self.required_dirs:
                full_path = self.base_dir / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directory created or exists: {full_path}")
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            sys.exit(1)

    def verify_dns(self, domain: str, retries: int = 3, delay: int = 10) -> bool:
        """Verify DNS configuration for domain with retries."""
        for attempt in range(retries):
            try:
                socket.gethostbyname(domain)
                return True
            except socket.gaierror:
                if attempt < retries - 1:
                    logger.warning(f"DNS verification failed for {domain}, retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    return False

    def setup_ssl(self, retries: int = 1) -> bool:
        """Set up SSL certificates using Certbot."""
        try:
            if not self.certbot_path.exists():
                logger.error(f"Certbot not found at {self.certbot_path}")
                logger.error("Please install Certbot using 'winget install certbot'")
                return False

            domains = [
                "statista.live",
                "api.statista.live",
                "monitor.statista.live"
            ]

            # Verify DNS for all domains
            dns_issues = []
            for domain in domains:
                if not self.verify_dns(domain):
                    dns_issues.append(domain)

            if dns_issues:
                logger.error("DNS verification failed for the following domains:")
                for domain in dns_issues:
                    logger.error(f"  - {domain}")
                logger.error("\nPlease ensure:")
                logger.error("1. Domain DNS records are properly configured")
                logger.error("2. DNS changes have propagated (may take up to 48 hours)")
                logger.error("3. Your domains point to the correct IP address")
                return False

            email = input("Enter your email for SSL certificate registration: ")
            
            cmd = [
                str(self.certbot_path),
                "certonly",
                "--standalone",
                "--preferred-challenges", "http",
                "--agree-tos",
                "--email", email
            ] + [item for domain in domains for item in ("-d", domain)]

            for attempt in range(retries):
                logger.info(f"Running Certbot (attempt {attempt + 1}/{retries})...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("SSL certificates generated successfully")
                    
                    cert_path = Path(r"C:\Certbot\live\statista.live")
                    if not cert_path.exists():
                        logger.error(f"Certificates not found at {cert_path}")
                        return False

                    nginx_cert_path = self.base_dir / 'config' / 'services' / 'nginx' / 'certs'
                    nginx_cert_path.mkdir(parents=True, exist_ok=True)
                    
                    for cert_file in ["fullchain.pem", "privkey.pem"]:
                        shutil.copy2(cert_path / cert_file, nginx_cert_path / cert_file)
                    
                    logger.info(f"Certificates copied to {nginx_cert_path}")
                    return True
                else:
                    logger.error(f"Certbot failed: {result.stderr}")
                    if attempt < retries - 1:
                        logger.info("Retrying SSL setup...")
                    else:
                        return False

        except Exception as e:
            logger.error(f"SSL setup failed: {e}")
            return False

    def setup_auth(self):
        """Set up authentication credentials."""
        try:
            username = input("Enter username for dashboard access: ")
            password = input("Enter password for dashboard access: ")

            if len(password) < 8:
                logger.error("Password must be at least 8 characters long.")
                sys.exit(1)

            salt = secrets.token_bytes(16)
            hashed_pw = self.hash_password(password, salt)

            htpasswd_path = self.base_dir / 'config' / 'services' / 'nginx' / '.htpasswd'
            htpasswd_path.parent.mkdir(parents=True, exist_ok=True)
            with open(htpasswd_path, 'w') as f:
                f.write(f"{username}:{hashed_pw}\n")
            logger.info(f"Authentication credentials created at {htpasswd_path}")

        except Exception as e:
            logger.error(f"Failed to set up authentication: {e}")
            sys.exit(1)

    def generate_secrets(self):
        """Generate secret keys and configuration variables."""
        secrets_file = self.base_dir / 'config' / 'secrets.json'
        try:
            secrets_data = {
                'SECRET_KEY': self.generate_secret_key(),
                'REDIS_PASSWORD': self.generate_password(),
                'GRAFANA_ADMIN_USER': 'admin',
                'GRAFANA_ADMIN_PASSWORD': self.generate_password(),
                'AI_DATA_PATH': str(self.base_dir / 'data' / 'ai'),
                'MODEL_CACHE_PATH': str(self.base_dir / 'data' / 'models')
            }
            with open(secrets_file, 'w') as f:
                json.dump(secrets_data, f, indent=4)
            logger.info(f"Secrets generated at {secrets_file}")
        except Exception as e:
            logger.error(f"Failed to generate secrets: {e}")
            sys.exit(1)

    def hash_password(self, password: str, salt: bytes) -> str:
        """Hash password using SHA256."""
        import hashlib
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt.hex() + dk.hex()

    def generate_secret_key(self, length: int = 50) -> str:
        """Generate a Django-style SECRET_KEY."""
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join(secrets.choice(chars) for _ in range(length))

    def generate_password(self, length: int = 12) -> str:
        """Generate a random password."""
        chars = string.ascii_letters + string.digits + '!@#$%^&*()'
        return ''.join(secrets.choice(chars) for _ in range(length))

if __name__ == "__main__":
    setup = SystemSetup()
    setup.setup_all()