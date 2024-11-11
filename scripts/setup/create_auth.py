# Location: E:/justica/scripts/setup/create_auth.py

import bcrypt
import os
from pathlib import Path

def create_htpasswd():
    # Define paths
    nginx_dir = Path("config/services/nginx")
    htpasswd_path = nginx_dir / ".htpasswd"

    # Create directory if it doesn't exist
    nginx_dir.mkdir(parents=True, exist_ok=True)

    # Generate password hash
    username = "fixola"
    password = "As!101010"
    
    # Generate bcrypt hash
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    # Create htpasswd file
    try:
        with open(htpasswd_path, "w") as f:
            f.write(f"{username}:{hashed}\n")
        print(f"Created .htpasswd at {htpasswd_path.absolute()}")
    except Exception as e:
        print(f"Error creating .htpasswd: {e}")

if __name__ == "__main__":
    create_htpasswd()