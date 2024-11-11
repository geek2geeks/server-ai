# scripts/utils/generate_secrets.py
import secrets
import string
import bcrypt
import base64
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_secure_password(length: int = 32) -> str:
    """Generate a cryptographically secure password."""
    try:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    except Exception as e:
        logger.error(f"Error generating password: {e}")
        raise

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    try:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise

def main():
    """Generate and save secure secrets for the application."""
    try:
        # Generate secrets
        secrets_dict = {
            'API_SECRET_KEY': generate_secure_password(48),
            'REDIS_PASSWORD': generate_secure_password(32),
            'POSTGRES_PASSWORD': generate_secure_password(32),
            'GRAFANA_ADMIN_PASSWORD': generate_secure_password(32),
            'PROMETHEUS_BASIC_AUTH_PASS': generate_secure_password(32),
        }
        
        # Create secrets file
        secrets_path = Path('../config/secrets/.env.secrets')
        secrets_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(secrets_path, 'w') as f:
            for key, value in secrets_dict.items():
                f.write(f'{key}={value}\n')
                if key == 'PROMETHEUS_BASIC_AUTH_PASS':
                    hashed = hash_password(value)
                    f.write(f'PROMETHEUS_BASIC_AUTH_PASS_HASH={hashed}\n')
        
        logger.info(f"Secrets generated and saved to {secrets_path}")
        
    except Exception as e:
        logger.error(f"Error generating secrets: {e}")
        raise

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)