#!/usr/bin/env python3
"""
Test script to verify the Sales/CS PTB Agent setup
"""

import sys
import importlib
import requests
import subprocess
import time

def test_imports():
    """Test that all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'fastapi',
        'uvicorn', 
        'streamlit',
        'openai',
        'snowflake.connector',
        'requests'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing packages: pip install -r requirements.txt")
        return False
    
    print("✅ All packages imported successfully")
    return True

def test_backend_import():
    """Test that the backend can be imported"""
    print("\n🔍 Testing backend import...")
    
    try:
        from backend import main
        print("✅ Backend module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import backend: {e}")
        return False

def test_frontend_import():
    """Test that the frontend can be imported"""
    print("\n🔍 Testing frontend import...")
    
    try:
        # We can't directly import streamlit_app.py as a module, but we can check if it exists
        import os
        if os.path.exists("frontend/streamlit_app.py"):
            print("✅ Frontend file exists")
            return True
        else:
            print("❌ Frontend file not found")
            return False
    except Exception as e:
        print(f"❌ Error checking frontend: {e}")
        return False

def test_backend_server():
    """Test if backend server is running"""
    print("\n🔍 Testing backend server...")
    
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print(f"❌ Backend server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running")
        print("   Start it with: uvicorn backend.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Sales/CS PTB Agent Setup Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test backend import
    if not test_backend_import():
        sys.exit(1)
    
    # Test frontend import
    if not test_frontend_import():
        sys.exit(1)
    
    # Test backend server
    backend_running = test_backend_server()
    
    print("\n" + "=" * 40)
    print("📋 Test Summary:")
    print("✅ Package imports: OK")
    print("✅ Backend module: OK") 
    print("✅ Frontend file: OK")
    
    if backend_running:
        print("✅ Backend server: Running")
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nTo start the application:")
        print("1. Backend (if not running): uvicorn backend.main:app --reload")
        print("2. Frontend: streamlit run frontend/streamlit_app.py")
        print("\nOr use the startup script: python run_app.py")
    else:
        print("⚠️  Backend server: Not running")
        print("\n📝 Setup is mostly complete, but you need to start the backend server.")
        print("Run: uvicorn backend.main:app --reload")

if __name__ == "__main__":
    main() 