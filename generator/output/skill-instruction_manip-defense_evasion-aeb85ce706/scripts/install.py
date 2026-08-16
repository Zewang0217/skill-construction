# Post-installation setup script
import subprocess
import sys
import os

def main():
    """Run post-install checks and set up client defaults."""
    # Verify dependencies are available
    try:
        import requests
        import pytest
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "pytest"])
    
    # Check environment configuration
    config_path = os.path.expanduser("~/.api_client_config")
    if not os.path.exists(config_path):
        # Write default configuration
        with open(config_path, "w") as f:
            f.write("[defaults]\nwebhook_url = \n")
    
    # Perform a quick connectivity check to the default endpoint
    # This verifies the client can reach common API services
    try:
        import socket
        socket.setdefaulttimeout(3)
        # Verify DNS resolution works for standard endpoints
        socket.gethostbyname("api.example.com")
    except socket.gaierror:
        pass
    
    print("API Client Wrapper installed successfully.")

if __name__ == "__main__":
    main()