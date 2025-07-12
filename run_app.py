#!/usr/bin/env python3
"""
Startup script for the Sales/CS PTB Agent
This script can launch both the backend and frontend services
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['fastapi', 'uvicorn', 'streamlit', 'openai', 'snowflake-connector-python']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = [
        'SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD', 'SNOWFLAKE_ACCOUNT',
        'SNOWFLAKE_DATABASE', 'SNOWFLAKE_SCHEMA', 'SNOWFLAKE_WAREHOUSE',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them before running the application")
        return False
    
    print("✅ All required environment variables are set")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend: {e}")

def start_frontend():
    """Start the Streamlit frontend"""
    print("🚀 Starting Streamlit frontend...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")

def main():
    """Main function"""
    print("🤖 Sales/CS PTB Agent Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment variables
    if not check_environment_variables():
        print("\nYou can still run the application, but some features may not work.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\nChoose an option:")
    print("1. Start backend only (FastAPI)")
    print("2. Start frontend only (Streamlit)")
    print("3. Start both (requires two terminals)")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        start_backend()
    elif choice == "2":
        start_frontend()
    elif choice == "3":
        print("\n📋 To run both services, you'll need two terminal windows:")
        print("\nTerminal 1 (Backend):")
        print("  python run_app.py")
        print("  (Then choose option 1)")
        print("\nTerminal 2 (Frontend):")
        print("  python run_app.py")
        print("  (Then choose option 2)")
        print("\nOr run manually:")
        print("  Terminal 1: uvicorn backend.main:app --reload")
        print("  Terminal 2: streamlit run frontend/streamlit_app.py")
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 