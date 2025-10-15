#!/usr/bin/env python3
"""
Trading Platform Modern - Setup Script
Automated setup script for the trading platform
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_requirements():
    """Install Python requirements"""
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    requirements_file = backend_dir / "requirements.txt"
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"pip install -r {requirements_file}",
        "Installing Python requirements"
    )

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "data",
        "backups",
        "cache",
        "frontend/icons"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists, skipping creation")
        return True
    
    env_content = """# Database Configuration
DATABASE_URL=mysql://root:password@localhost:3306/scalper
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=scalper

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379

# Application Configuration
APP_NAME=Trading Platform Modern
DEBUG=True
SECRET_KEY=your-secret-key-change-this
ENVIRONMENT=development

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Trading Platform Modern

# WebSocket Configuration
WEBSOCKET_URL=ws://localhost:8000/socket.io

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Data Sources
YAHOO_FINANCE_ENABLED=True
WEB_SCRAPING_ENABLED=True

# Cache Configuration
CACHE_TTL=3600

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256

# Trading Configuration
TRAINING_MODE=True
AUTO_TRADING=False
DEFAULT_CURRENCY=IDR
DEFAULT_TIMEZONE=Asia/Jakarta
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    dependencies = [
        ("mysql", "MySQL database"),
        ("redis-server", "Redis server"),
        ("python3", "Python 3.8+")
    ]
    
    print("🔍 Checking system dependencies...")
    missing_deps = []
    
    for dep, description in dependencies:
        if not run_command(f"which {dep}", f"Checking {description}"):
            missing_deps.append(f"{dep} ({description})")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPlease install missing dependencies before continuing.")
        return False
    
    return True

def setup_database():
    """Setup database schema"""
    print("🗄️  Setting up database...")
    print("Please ensure MySQL is running and create a database named 'scalper'")
    print("You can do this by running:")
    print("   mysql -u root -p")
    print("   CREATE DATABASE scalper;")
    print("   exit")
    
    response = input("Have you created the database? (y/n): ")
    if response.lower() != 'y':
        print("❌ Please create the database first")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Trading Platform Modern - Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check system dependencies
    if not check_dependencies():
        print("\n📋 Installation Instructions:")
        print("Ubuntu/Debian:")
        print("   sudo apt update")
        print("   sudo apt install mysql-server redis-server python3-pip")
        print("\nCentOS/RHEL:")
        print("   sudo yum install mysql-server redis python3-pip")
        print("\nmacOS:")
        print("   brew install mysql redis python3")
        print("\nWindows:")
        print("   Download MySQL and Redis from their official websites")
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Create .env file
    print("\n⚙️  Creating configuration...")
    if not create_env_file():
        sys.exit(1)
    
    # Install Python requirements
    print("\n📦 Installing Python packages...")
    if not install_requirements():
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    # Setup database
    print("\n🗄️  Database setup...")
    if not setup_database():
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your database credentials")
    print("2. Start MySQL and Redis services")
    print("3. Run the application:")
    print("   cd backend")
    print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("4. Open http://localhost:8000 in your browser")
    print("\n📚 Documentation: README.md")
    print("🐛 Issues: GitHub Issues")

if __name__ == "__main__":
    main()
