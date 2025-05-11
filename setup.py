#!/usr/bin/env python
"""
JobSniffer setup script.

This script helps prepare the environment for running the application.
It checks dependencies, creates necessary directories, and sets up configuration.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

def check_python_version():

    print("Checking Python version...")
    
    major, minor, _, _, _ = sys.version_info
    if major < 3 or (major == 3 and minor < 10):
        print(f"Error: Python 3.10+ is required. Current version is {major}.{minor}")
        return False
    
    print(f"Python version {major}.{minor} is compatible.")
    return True

def check_postgresql():

    print("Checking PostgreSQL...")
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["pg_isready"], capture_output=True, text=True)
        else:
            result = subprocess.run(["pg_isready", "-U", "postgres"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("PostgreSQL is installed and running.")
            return True
        else:
            print("PostgreSQL is installed but not running or not accessible.")
            return False
    except FileNotFoundError:
        print("PostgreSQL is not installed or not in PATH.")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("Checking .env file...")
    
    env_path = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_path):
        print(".env file already exists.")
        return True
    
    print("Creating .env file...")
    env_content = """DATABASE_URL=postgresql://postgres:postgres@localhost/jobsniffer
    JWT_SECRET_KEY=
    JWT_ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    OPENAI_API_KEY=
    REDIS_URL=redis://localhost:6379/0
    RABBITMQ_URL=amqp://guest:guest@localhost:5672/
    INDEED_API_KEY=
    LINKEDIN_API_KEY=
    """
    
    try:
        with open(env_path, "w") as f:
            f.write(env_content)
        print(".env file created successfully.")
        print("Please update the .env file with your actual credentials.")
        return True
    except Exception as e:
        print(f"Error creating .env file: {e}")
        return False

def create_directories():
    """Create necessary directories if they don't exist"""
    print("Creating necessary directories...")
    
    directories = [
        os.path.join(ROOT_DIR, "static"),
        os.path.join(ROOT_DIR, "mock_data"),
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    
    try:
        # First install core dependencies
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "core_requirements.txt"])
        if result.returncode != 0:
            print("Error installing core dependencies.")
            return False
        
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        if result.returncode != 0:
            print("Error installing dependencies.")
            return False
        
        print("Dependencies installed successfully.")
        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False

def setup():
    """Run setup process"""
    print("="*80)
    print("JobSniffer Setup")
    print("="*80)
    
    if not check_python_version():
        print("Please upgrade Python to version 3.10 or higher.")
        return False
    
    pg_available = check_postgresql()
    if not pg_available:
        print("PostgreSQL is not available. You can still run the application with mock database.")
    
    if not create_directories():
        print("Error creating directories.")
        return False
    
    if not create_env_file():
        print("Error creating .env file.")
        return False
    
    if not install_dependencies():
        print("Error installing dependencies.")
        return False
    
    print("="*80)
    print("Setup completed successfully!")
    print("="*80)
    
    print("\nInstructions:")
    print("-"*80)
    if pg_available:
        print("1. Update the .env file with your actual credentials")
        print("2. Initialize the database: python run_app.py --init-db")
        print("3. Start the application: python run_app.py")
    else:
        print("1. Update the .env file (especially OPENAI_API_KEY for AI features)")
        print("2. Start with mock database: python run_app.py --mock")
    
    print("\nAccess the application:")
    print("- API documentation: http://localhost:8000/docs")
    print("- Web UI: http://localhost:8000/ui")
    
    return True

if __name__ == "__main__":
    setup() 