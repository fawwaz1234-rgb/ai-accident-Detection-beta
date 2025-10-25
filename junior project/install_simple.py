#!/usr/bin/env python3
"""
Simple Dependency Installer for AI Accident Detection System
This version avoids problematic packages and focuses on core functionality
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

def install_core_only():
    """Install only the core packages that work reliably"""
    print("🔧 Installing core packages only...")
    
    core_packages = [
        "flask>=2.3.0",
        "flask-cors>=4.0.0", 
        "flask-jwt-extended>=4.5.0",
        "requests>=2.28.0",
        "bcrypt>=4.0.0",
        "python-dotenv>=1.0.0",
        "pillow>=9.0.0",
        "numpy>=1.21.0"
    ]
    
    for package in core_packages:
        run_command(f"pip install {package}", f"Installing {package}")

def install_opencv_alternative():
    """Install OpenCV with fallback options"""
    print("👁️ Installing computer vision packages...")
    
    # Try different OpenCV versions
    opencv_options = [
        "opencv-python-headless",
        "opencv-python==4.8.1.78", 
        "opencv-python"
    ]
    
    for opencv in opencv_options:
        if run_command(f"pip install {opencv}", f"Installing {opencv}"):
            break
        else:
            print(f"⚠️ {opencv} failed, trying next option...")

def install_ultralytics_alternative():
    """Install YOLOv8 with fallback options"""
    print("🤖 Installing AI packages...")
    
    # Try to install ultralytics without torch dependency issues
    if not run_command("pip install ultralytics --no-deps", "Installing Ultralytics (no dependencies)"):
        print("⚠️ Ultralytics installation failed, system will use demo mode")
    
    # Try to install torch separately with CPU-only version
    if not run_command("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu", "Installing PyTorch (CPU only)"):
        print("⚠️ PyTorch installation failed, system will use demo mode")

def install_optional():
    """Install optional packages"""
    print("🔧 Installing optional packages...")
    
    optional_packages = [
        "geopy",
        "pymongo", 
        "firebase-admin",
        "twilio"
    ]
    
    for package in optional_packages:
        run_command(f"pip install {package}", f"Installing {package} (optional)")

def test_core_functionality():
    """Test if core functionality works"""
    print("\n🧪 Testing core functionality...")
    
    test_imports = [
        ("flask", "Flask web framework"),
        ("requests", "HTTP requests"),
        ("bcrypt", "Password hashing"),
        ("PIL", "Image processing"),
        ("numpy", "Numerical computing")
    ]
    
    success_count = 0
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} - OK")
            success_count += 1
        except ImportError:
            print(f"❌ {name} - Missing")
    
    # Test OpenCV
    try:
        import cv2
        print("✅ OpenCV - OK")
        success_count += 1
    except ImportError:
        print("❌ OpenCV - Missing (will use demo mode)")
    
    # Test YOLOv8 (optional)
    try:
        import ultralytics
        print("✅ YOLOv8 - OK")
        success_count += 1
    except ImportError:
        print("❌ YOLOv8 - Missing (will use demo mode)")
    
    print(f"\n📊 Core functionality: {success_count}/{len(test_imports)+2} packages working")
    return success_count >= 4

def main():
    """Main installation function"""
    print("🚗 AI Accident Detection - Simple Installer")
    print("=" * 50)
    print("This installer avoids problematic packages and focuses on core functionality")
    print("=" * 50)
    
    # Install core packages
    install_core_only()
    
    # Install computer vision
    install_opencv_alternative()
    
    # Install AI packages
    install_ultralytics_alternative()
    
    # Install optional packages
    install_optional()
    
    # Test installation
    success = test_core_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Installation completed successfully!")
        print("\n🚀 You can now run the application:")
        print("   python app.py")
        print("\n🌐 Then open: http://localhost:5000")
        print("👤 Login with: admin / admin123")
        print("\n💡 The system will work in demo mode if some AI packages are missing.")
    else:
        print("⚠️ Some packages failed, but you can still try running the app.")
        print("💡 The system is designed to work even with missing packages.")
    
    return success

if __name__ == "__main__":
    main()
