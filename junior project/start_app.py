#!/usr/bin/env python3
"""
Simple script to start the AI Accident Detection app
"""

print("🚗 Starting AI Accident Detection System...")
print("=" * 50)

try:
    from app import app
    print("✅ App imported successfully")
    print("🌐 Starting server on http://localhost:5000")
    print("👤 Login with: admin / admin123")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
    
except Exception as e:
    print(f"❌ Error starting app: {e}")
    print("💡 The app will work in demo mode")
    print("🌐 Try opening http://localhost:5000 in your browser")
