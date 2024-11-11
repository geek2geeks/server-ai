# Location: /scripts/setup/ssl_auth.py

import subprocess
import bcrypt
import ctypes
import sys
from pathlib import Path
import os
import shutil

# Setup base directories
ROOT_DIR = Path('E:/justica')
LOGS_DIR = ROOT_DIR / "logs"
CONFIG_DIR = ROOT_DIR / "config"
NGINX_DIR = CONFIG_DIR / "services" / "nginx"
CERTBOT_DIR = Path(r"C:\Program Files\Certbot\bin\certbot.exe")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_privileges():
    if not is_admin():
        print("Script needs to be run with administrative privileges.")
        print("Please right-click on PowerShell/Command Prompt and select 'Run as administrator'")
        print("Then run this script again.")
        input("Press Enter to exit...")
        sys.exit(1)

def setup_ssl_certs():
    """Generate SSL certificates using Let's Encrypt"""
    if not CERTBOT_DIR.exists():
        print(f"Certbot not found at {CERTBOT_DIR}")
        print("Please install using: winget install certbot")
        return False

    email = input("Enter email for SSL certificate notifications: ")
    
    cmd = [
        str(CERTBOT_DIR),
        "certonly",
        "--standalone",
        "--preferred-challenges", "http",
        "--agree-tos",
        "--email", email,
        "-d", "statista.live",
        "-d", "api.statista.live",
        "-d", "monitor.statista.live"
    ]
    
    try:
        print("Running certbot...")
        result = subprocess.run(cmd, 
                              check=True,
                              capture_output=True,
                              text=True)
        print("SSL certificates generated successfully")
        
        cert_path = Path(r"C:\Certbot\live\statista.live")
        if cert_path.exists():
            nginx_certs = NGINX_DIR / "certs"
            nginx_certs.mkdir(parents=True, exist_ok=True)
            
            for cert_file in ["fullchain.pem", "privkey.pem"]:
                shutil.copy2(cert_path / cert_file, nginx_certs / cert_file)
                print(f"Copied {cert_file} to nginx certs directory")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate certificates: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_auth_credentials():
    """Create authentication credentials for Nginx"""
    try:
        username = input("Enter username for dashboard access: ")
        password = input("Enter password for dashboard access: ")
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        
        htpasswd_path = NGINX_DIR / ".htpasswd"
        with open(htpasswd_path, "w") as f:
            f.write(f"{username}:{hashed.decode()}\n")
        
        print(f"Created authentication file at {htpasswd_path}")
        return True
    except Exception as e:
        print(f"Failed to create credentials: {e}")
        return False

def main():
    # Check admin rights
    elevate_privileges()

    print("\n=== Starting SSL and authentication setup ===\n")
    
    # Create necessary directories
    NGINX_DIR.mkdir(parents=True, exist_ok=True)
    
    # Setup SSL certificates
    if not setup_ssl_certs():
        print("SSL certificate setup failed")
        return
    
    # Create authentication credentials
    if not create_auth_credentials():
        print("Authentication setup failed")
        return
    
    print("\n=== Setup completed successfully! ===")

if __name__ == "__main__":
    main()