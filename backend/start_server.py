#!/usr/bin/env python3
"""
Stable startup script for the Rockfall Detection Flask server
This script ensures proper environment setup and stable server operation
"""

import os
import sys
import subprocess
import time

def setup_environment():
    """Setup environment variables to prevent Flask restart issues"""
    env_vars = {
        'YOLO_VERBOSE': 'False', 
        'TOKENIZERS_PARALLELISM': 'false',
        'FLASK_ENV': 'production',
        'WERKZEUG_RUN_MAIN': 'true'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ Set {key}={value}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['flask', 'flask-cors', 'opencv-python', 'ultralytics', 'numpy', 'pillow']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install " + " ".join(missing))
        return False
    
    return True

def start_server():
    """Start the Flask server with proper configuration"""
    print("\n🚀 Starting Rockfall Detection Server...")
    print("🔥 Enhanced pit-only detection with size preservation")
    print("🏔️  Multi-stage pipeline with thermal visualization")
    print("📡 Server will be available at: http://localhost:5000")
    print("🖥️  Frontend should connect to: http://localhost:5000")
    print("\n" + "="*60)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(
            host="0.0.0.0", 
            port=5000, 
            debug=False,           # Disable debug to prevent auto-reload
            threaded=True,         # Enable threading for better performance
            use_reloader=False     # Explicitly disable reloader
        )
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Setting up environment...")
    setup_environment()
    
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print("\n📁 Checking project structure...")
    required_files = ['app.py', 'src/main.py', 'src/change_detection.py', 'src/segmentation.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        sys.exit(1)
    else:
        print("✅ All required files present")
    
    # Start the server
    start_server()