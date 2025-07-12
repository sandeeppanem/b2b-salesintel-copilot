#!/usr/bin/env python3
"""
Quick status checker for backend and frontend services
"""

import requests
import subprocess
import sys
import time

def check_port(port):
    """Check if a port is in use"""
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_backend():
    """Check backend status"""
    print("🔍 Checking Backend (Port 8000)...")
    
    # Check if port is in use
    if not check_port(8000):
        print("  ❌ Port 8000 is not in use")
        return False
    
    # Check if service is responding
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("  ✅ Backend is running and responding")
            return True
        else:
            print(f"  ⚠️  Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Backend is not responding")
        return False
    except Exception as e:
        print(f"  ❌ Error checking backend: {e}")
        return False

def check_frontend():
    """Check frontend status"""
    print("🔍 Checking Frontend (Port 8501)...")
    
    # Check if port is in use
    if not check_port(8501):
        print("  ❌ Port 8501 is not in use")
        return False
    
    # Check if service is responding
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("  ✅ Frontend is running and responding")
            return True
        else:
            print(f"  ⚠️  Frontend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Frontend is not responding")
        return False
    except Exception as e:
        print(f"  ❌ Error checking frontend: {e}")
        return False

def test_backend_api():
    """Test a simple API call"""
    print("🔍 Testing Backend API...")
    
    try:
        response = requests.get(
            "http://localhost:8000/api/opportunities",
            params={
                "user_id": "test_user",
                "opportunity_type": "cross_sell",
                "top_n": 1
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("  ✅ API call successful")
            return True
        elif response.status_code == 404:
            print("  ⚠️  API responded with 404 (expected if no data)")
            return True
        else:
            print(f"  ❌ API responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ API test failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Service Status Check")
    print("=" * 30)
    
    backend_ok = check_backend()
    frontend_ok = check_frontend()
    
    print("\n" + "=" * 30)
    print("📋 Status Summary:")
    print(f"Backend:  {'✅ Running' if backend_ok else '❌ Not Running'}")
    print(f"Frontend: {'✅ Running' if frontend_ok else '❌ Not Running'}")
    
    if backend_ok:
        test_backend_api()
    
    print("\n" + "=" * 30)
    if backend_ok and frontend_ok:
        print("🎉 All services are running!")
        print("\nAccess your application:")
        print("  Frontend: http://localhost:8501")
        print("  Backend API: http://localhost:8000/docs")
    else:
        print("⚠️  Some services are not running")
        print("\nTo start services:")
        print("  Backend:  uvicorn backend.main:app --reload")
        print("  Frontend: streamlit run frontend/streamlit_app.py")
        print("  Or use:   python run_app.py")

if __name__ == "__main__":
    main() 