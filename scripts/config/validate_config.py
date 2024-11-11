import os
import yaml
import redis
from pathlib import Path
from dotenv import load_dotenv

def validate_env():
    """Validate environment variables"""
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
            
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

def validate_redis_connection():
    """Test Redis connection with new configuration"""
    try:
        r = redis.Redis(
            host='localhost',
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            ssl=os.getenv('REDIS_TLS_ENABLED', 'true').lower() == 'true'
        )
        r.ping()
    except Exception as e:
        raise ConnectionError(f"Redis connection failed: {str(e)}")

def main():
    """Main validation function"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Validate environment
        validate_env()
        
        # Validate Redis
        validate_redis_connection()
        
        print("Configuration validation successful!")
        
    except Exception as e:
        print(f"Configuration validation failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()