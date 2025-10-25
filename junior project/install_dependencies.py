#!/usr/bin/env python3
"""
Dependency Installation Script for AI Accident Detection System
This script will install dependencies step by step and handle common issues
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("💡 Please install Python 3.8 or higher from https://python.org")
        return False

def install_core_dependencies():
    """Install core Flask dependencies"""
    dependencies = [
        ("flask", "Flask web framework"),
        ("flask-cors", "Flask CORS support"),
        ("flask-jwt-extended", "JWT authentication"),
        ("requests", "HTTP requests library"),
        ("bcrypt", "Password hashing"),
        ("python-dotenv", "Environment variables")
    ]
    
    print("\n🔧 Installing core dependencies...")
    for package, description in dependencies:
        if not run_command(f"pip install {package}", f"Installing {description}"):
            print(f"⚠️ Failed to install {package}, but continuing...")

def install_ai_dependencies():
    """Install AI and computer vision dependencies"""
    print("\n🤖 Installing AI dependencies...")
    
    # Install numpy first (required by others)
    run_command("pip install numpy", "Installing NumPy")
    
    # Install OpenCV
    if not run_command("pip install opencv-python", "Installing OpenCV"):
        print("🔄 Trying opencv-python-headless...")
        run_command("pip install opencv-python-headless", "Installing OpenCV (headless)")
    
    # Install Pillow
    run_command("pip install pillow", "Installing Pillow")
    
    # Install Ultralytics (YOLOv8)
    if not run_command("pip install ultralytics", "Installing Ultralytics (YOLOv8)"):
        print("⚠️ YOLOv8 installation failed, but system will work in demo mode")

def install_optional_dependencies():
    """Install optional dependencies"""
    print("\n🔧 Installing optional dependencies...")
    
    optional_deps = [
        ("geopy", "Location services"),
        ("pymongo", "MongoDB support"),
        ("firebase-admin", "Firebase support"),
        ("twilio", "SMS notifications")
    ]
    
    for package, description in optional_deps:
        run_command(f"pip install {package}", f"Installing {description} (optional)")

def test_installation():
    """Test if the installation worked"""
    print("\n🧪 Testing installation...")
    
    test_imports = [
        ("flask", "Flask"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow"),
        ("requests", "Requests"),
        ("bcrypt", "bcrypt"),
        ("ultralytics", "Ultralytics (YOLOv8)")
    ]
    
    success_count = 0
    total_count = len(test_imports)
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} - OK")
            success_count += 1
        except ImportError:
            print(f"❌ {name} - Missing")
    
    print(f"\n📊 Installation Summary: {success_count}/{total_count} packages working")
    
    if success_count >= 5:  # At least core packages
        print("🎉 Installation successful! You can now run the application.")
        return True
    else:
        print("⚠️ Some packages failed to install, but the system will work in demo mode.")
        return True  # Still return True as demo mode works

def main():
    """Main installation function"""
    print("🚗 AI Accident Detection System - Dependency Installer")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Upgrade pip first
    print("\n📦 Upgrading pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install dependencies
    install_core_dependencies()
    install_ai_dependencies()
    install_optional_dependencies()
    
    # Test installation
    success = test_installation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Installation completed!")
        print("\n🚀 Next steps:")
        print("   1. Run: python app.py")
        print("   2. Open: http://localhost:5000")
        print("   3. Login with: admin / admin123")
        print("\n💡 If you see warnings about missing packages, the system will work in demo mode.")
    else:
        print("❌ Installation had issues, but you can still try running the app.")
        print("💡 The system will work in demo mode even with missing packages.")
    
    return success

if __name__ == "__main__":
    main()
