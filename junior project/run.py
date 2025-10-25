#!/usr/bin/env python3
"""
AI-Powered Accident Detection System
Startup script for the hackathon project
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import flask
        import cv2
        import numpy
        from ultralytics import YOLO
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ['templates', 'static', 'models', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")

def setup_environment():
    """Set up environment variables"""
    print("⚙️ Setting up environment...")
    
    env_file = Path('.env')
    if not env_file.exists():
        config_file = Path('config.env')
        if config_file.exists():
            env_file.write_text(config_file.read_text())
            print("✅ Created .env file from config.env")
        else:
            # Create basic .env file
            env_content = """# AI Accident Detection Environment Variables
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
MONGODB_URI=mongodb://localhost:27017/accident_detection
GOOGLE_MAPS_API_KEY=
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=mabd95026@gmail.com
SMTP_PASSWORD=
ALERT_EMAILS=Mohammed375526@gmail.com
ALERT_COOLDOWN_SECONDS=20
"""
            env_file.write_text(env_content)
            print("✅ Created basic .env file")

def download_yolo_model():
    """Download YOLOv8 model if not present"""
    print("🤖 Checking YOLOv8 model...")
    
    model_path = Path('yolov8n.pt')
    if not model_path.exists():
        print("📥 Downloading YOLOv8 model...")
        try:
            from ultralytics import YOLO
            model = YOLO('yolov8n.pt')
            print("✅ YOLOv8 model downloaded")
        except Exception as e:
            print(f"⚠️ Could not download model: {e}")
            print("The model will be downloaded automatically on first run")
    else:
        print("✅ YOLOv8 model already exists")

# New helper: create a basic .gitignore if missing
def create_gitignore():
    gi = Path('.gitignore')
    if not gi.exists():
        gi.write_text("""# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd

# Environments
.env
.env.*
venv/
venv*/
env/

# IDEs
.vscode/
.idea/

# Logs and databases
logs/
*.sqlite3
*.db

# OS
.DS_Store
""")
        print("✅ Created .gitignore")
    else:
        print("ℹ️ .gitignore already exists")

# New helper: initialize git repo, commit and push to given remote_url.
def push_to_github(remote_url):
    """Initialize git, make initial commit (if necessary) and push to remote_url."""
    if not remote_url:
        print("❌ No remote URL provided for pushing. Set GIT_REMOTE_URL or pass --push <url>.")
        return

    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        print("❌ Git is not installed or not available in PATH. Install git to push automatically.")
        print(f"ℹ️ To push manually, run:\n  git init\n  git add .\n  git commit -m \"Initial commit\"\n  git remote add origin {remote_url}\n  git branch -M main\n  git push -u origin main")
        return

    try:
        # init repo if needed
        if not Path('.git').exists():
            subprocess.check_call(["git", "init"])
            print("✅ Initialized new git repository")

        # ensure .gitignore exists
        create_gitignore()

        # stage files
        subprocess.check_call(["git", "add", "."])
        # create a commit if there are changes to commit
        try:
            subprocess.check_call(["git", "commit", "-m", "Initial commit"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Created initial commit")
        except subprocess.CalledProcessError:
            # commit failed (likely nothing to commit or already committed) -> continue
            print("ℹ️ Nothing to commit or already committed")

        # set remote
        # remove existing origin to avoid duplicate remote error
        subprocess.run(["git", "remote", "remove", "origin"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.check_call(["git", "remote", "add", "origin", remote_url])
        subprocess.check_call(["git", "branch", "-M", "main"])
        # push
        subprocess.check_call(["git", "push", "-u", "origin", "main"])
        print("✅ Pushed repository to", remote_url)
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
        print("ℹ️ You can push manually with the commands mentioned above.")

def start_application():
    """Start the Flask application"""
    print("🚀 Starting AI Accident Detection System...")
    print("=" * 50)
    print("🎯 HACKATHON PROJECT: AI-Powered Accident Detection")
    print("🌐 Web Interface: http://localhost:5000")
    print("📱 Demo Accounts:")
    print("   Admin: admin / admin123")
    print("   User:  user / user123")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main startup function"""
    print("🚗 AI-Powered Accident Detection System")
    print("🏆 Hackathon Project - Safer Indian Highways")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('app.py').exists():
        print("❌ app.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Setup steps
    create_directories()
    setup_environment()
    
    # create .gitignore (safe no-op if already present)
    create_gitignore()

    # If user wants to push to GitHub:
    # - Command-line: --push <remote_url>
    # - Or environment variable: GIT_REMOTE_URL
    git_remote = None
    if "--push" in sys.argv:
        try:
            idx = sys.argv.index("--push")
            git_remote = sys.argv[idx+1] if len(sys.argv) > idx+1 else None
        except Exception:
            git_remote = None
    if not git_remote:
        git_remote = os.environ.get("GIT_REMOTE_URL")

    if git_remote:
        print(f"🔗 Pushing code to remote: {git_remote}")
        push_to_github(git_remote)
    else:
        print("ℹ️ Not pushing to GitHub automatically. To push now run this script with:")
        print("   python run.py --push <your-git-remote-url>")
        print("Or set environment variable GIT_REMOTE_URL and re-run.")

    if check_dependencies():
        download_yolo_model()
        start_application()
    else:
        print("❌ Setup failed. Please install dependencies manually:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()

