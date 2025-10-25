# 📦 Installation Guide - AI Accident Detection System

## 🚨 If you're getting errors, follow this step-by-step guide:

### Step 1: Install Python (if not already installed)
- Download Python 3.8+ from https://python.org
- Make sure to check "Add Python to PATH" during installation
- Verify installation: `python --version`

### Step 2: Install Dependencies (Choose one method)

#### Method A: Minimal Installation (Recommended for first try)
```bash
# Install only essential packages
pip install -r requirements-minimal.txt
```

#### Method B: Full Installation
```bash
# Install all packages
pip install -r requirements.txt
```

#### Method C: Manual Installation (if above fails)
```bash
# Install packages one by one
pip install flask
pip install flask-cors
pip install flask-jwt-extended
pip install opencv-python
pip install ultralytics
pip install numpy
pip install pillow
pip install requests
pip install bcrypt
pip install python-dotenv
pip install geopy
```

### Step 3: Handle Common Issues

#### Issue 1: OpenCV Installation Error
```bash
# Try this instead
pip install opencv-python-headless
```

#### Issue 2: TensorFlow Issues
```bash
# Skip TensorFlow for now (it's optional)
# The system works without it
```

#### Issue 3: Permission Errors
```bash
# On Windows, run as Administrator
# Or use user installation
pip install --user -r requirements-minimal.txt
```

#### Issue 4: Python Version Issues
```bash
# Make sure you're using Python 3.8+
python --version
# If not, install Python 3.8+ from python.org
```

### Step 4: Test Installation
```bash
# Run the test script
python test_system.py
```

### Step 5: Start the Application
```bash
# Start the system
python app.py
```

## 🔧 Troubleshooting

### Error: "No module named 'cv2'"
```bash
pip install opencv-python
# or
pip install opencv-python-headless
```

### Error: "No module named 'ultralytics'"
```bash
pip install ultralytics
```

### Error: "No module named 'flask'"
```bash
pip install flask flask-cors flask-jwt-extended
```

### Error: "No module named 'bcrypt'"
```bash
pip install bcrypt
```

### Error: "Permission denied"
- On Windows: Run Command Prompt as Administrator
- On Mac/Linux: Use `sudo pip install` (not recommended)

### Error: "pip not found"
- Install pip: `python -m ensurepip --upgrade`
- Or download get-pip.py and run it

## 🎯 Quick Start (If Everything Works)

1. **Install minimal requirements:**
   ```bash
   pip install -r requirements-minimal.txt
   ```

2. **Start the application:**
   ```bash
   python app.py
   ```

3. **Open browser to:**
   ```
   http://localhost:5000
   ```

4. **Login with:**
   - Username: `admin`
   - Password: `admin123`

## 📱 Alternative: Use Virtual Environment

If you're having dependency conflicts:

```bash
# Create virtual environment
python -m venv accident_detection_env

# Activate it
# On Windows:
accident_detection_env\Scripts\activate
# On Mac/Linux:
source accident_detection_env/bin/activate

# Install dependencies
pip install -r requirements-minimal.txt

# Run the app
python app.py
```

## 🆘 Still Having Issues?

### Check Python Version
```bash
python --version
# Should be 3.8 or higher
```

### Check pip Version
```bash
pip --version
# Update if needed: python -m pip install --upgrade pip
```

### Clear pip cache
```bash
pip cache purge
```

### Install with no cache
```bash
pip install --no-cache-dir -r requirements-minimal.txt
```

## ✅ Success Indicators

You'll know it's working when:
1. No error messages during installation
2. `python app.py` starts without errors
3. Browser shows the landing page at http://localhost:5000
4. You can login with admin/admin123

## 🎉 Ready to Demo!

Once everything is installed:
1. Run `python app.py`
2. Open http://localhost:5000
3. Login and explore the features
4. Start the live camera for real-time detection

**The system will work even without optional services like Twilio or Firebase!**
