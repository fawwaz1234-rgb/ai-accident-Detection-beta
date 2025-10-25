from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import base64
import io
import json
import os
from datetime import datetime
import threading
import time
import requests
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import smtplib
from email.message import EmailMessage

# Optional imports - handle gracefully if not available
try:
    import cv2
    import numpy as np
    from PIL import Image
    COMPUTER_VISION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Computer vision libraries not available: {e}")
    print("💡 Install with: pip install opencv-python pillow numpy")
    COMPUTER_VISION_AVAILABLE = False

# Try to import YOLO separately to avoid PyTorch issues
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ YOLOv8 not available: {e}")
    print("💡 Install with: pip install ultralytics")
    YOLO_AVAILABLE = False
except OSError as e:
    print(f"⚠️ YOLOv8 has dependency issues: {e}")
    print("💡 System will use demo mode for AI detection")
    YOLO_AVAILABLE = False

try:
    from geopy.geocoders import Nominatim
    LOCATION_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Location services not available: {e}")
    print("💡 Install with: pip install geopy")
    LOCATION_SERVICES_AVAILABLE = False

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Twilio not available: {e}")
    print("💡 Install with: pip install twilio")
    TWILIO_AVAILABLE = False

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Firebase not available: {e}")
    print("💡 Install with: pip install firebase-admin")
    FIREBASE_AVAILABLE = False

try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MongoDB not available: {e}")
    print("💡 Install with: pip install pymongo")
    MONGODB_AVAILABLE = False

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
jwt = JWTManager(app)

# Initialize Firebase
if FIREBASE_AVAILABLE:
    try:
        cred = credentials.Certificate('firebase-credentials.json')
        firebase_admin.initialize_app(cred)
        db_firestore = firestore.client()
        print("✅ Firebase initialized")
    except:
        print("⚠️ Firebase credentials not found. Using in-memory storage.")
        db_firestore = None
else:
    db_firestore = None

# Initialize MongoDB
if MONGODB_AVAILABLE:
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000, connectTimeoutMS=3000)
        client.admin.command('ping')
        db_mongo = client['accident_detection']
        users_collection = db_mongo['users']
        accidents_collection = db_mongo['accidents']
        print("✅ MongoDB initialized")
    except Exception as e:
        print(f"⚠️ MongoDB not available. Using in-memory storage. Reason: {e}")
        db_mongo = None
        users_collection = None
        accidents_collection = None
else:
    db_mongo = None
    users_collection = None
    accidents_collection = None

# Load YOLOv8 model
if COMPUTER_VISION_AVAILABLE and YOLO_AVAILABLE:
    try:
        model = YOLO('yolov8n.pt')
        print("✅ YOLOv8 model loaded")
    except Exception as e:
        print(f"⚠️ Could not load YOLOv8 model: {e}")
        model = None
else:
    model = None
    if not YOLO_AVAILABLE:
        print("⚠️ YOLOv8 not available - using demo mode")

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')

if TWILIO_AVAILABLE and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("✅ Twilio initialized")
    except Exception as e:
        print(f"⚠️ Twilio initialization failed: {e}")
        twilio_client = None
else:
    twilio_client = None
    if not TWILIO_AVAILABLE:
        print("⚠️ Twilio not available. Install with: pip install twilio")
    else:
        print("⚠️ Twilio credentials not configured")

# SMTP email configuration
SMTP_HOST = os.getenv('SMTP_HOST', '')
try:
    SMTP_PORT = int(os.getenv('SMTP_PORT', '0') or 0)
except Exception:
    SMTP_PORT = 0
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
ALERT_EMAILS = [e.strip() for e in os.getenv('ALERT_EMAILS', '').split(',') if e.strip()]

def send_email_alert(subject, body):
    try:
        if not (SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASSWORD and ALERT_EMAILS):
            return False
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = ', '.join(ALERT_EMAILS)
        msg.set_content(body)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False

# Alert cooldown configuration
try:
    ALERT_COOLDOWN_SECONDS = int(os.getenv('ALERT_COOLDOWN_SECONDS', '20') or 20)
except Exception:
    ALERT_COOLDOWN_SECONDS = 20
last_alert_time = 0

# In-memory storage for demo
users_db = {}
accidents_db = []
current_location = {"lat": 28.6139, "lng": 77.2090}  # Default to Delhi

# Create demo users
def create_demo_users():
    """Create demo users for testing"""
    demo_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
    users_db['admin'] = {
        'password': demo_password,
        'email': 'admin@accidentdetection.com',
        'role': 'admin',
        'created_at': datetime.now().isoformat()
    }
    
    demo_password2 = bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt())
    users_db['user'] = {
        'password': demo_password2,
        'email': 'user@accidentdetection.com',
        'role': 'user',
        'created_at': datetime.now().isoformat()
    }
    
    print("✅ Demo users created:")
    print("   Admin - Username: admin, Password: admin123")
    print("   User - Username: user, Password: user123")

# Initialize demo users
create_demo_users()

def seed_sample_data():
    """Seed sample accident records once at startup"""
    try:
        sample_accidents = [
            {
                "timestamp": datetime.now().isoformat(),
                "location": "Connaught Place, New Delhi, India",
                "coordinates": {"lat": 28.6315, "lng": 77.2167},
                "confidence": 0.82,
                "vehicles_detected": 2,
                "status": "alert_sent",
            },
            {
                "timestamp": datetime.now().isoformat(),
                "location": "MG Road, Gurugram, India",
                "coordinates": {"lat": 28.4793, "lng": 77.0737},
                "confidence": 0.67,
                "vehicles_detected": 1,
                "status": "alert_sent",
            },
        ]

        # Prefer Firestore if available
        if db_firestore is not None:
            try:
                acc_ref = db_firestore.collection('accidents')
                existing = list(acc_ref.limit(1).stream())
                if not existing:
                    for rec in sample_accidents:
                        acc_ref.add(rec)
                    print("✅ Seeded sample accidents to Firestore")
                return
            except Exception:
                pass

        # Next, try MongoDB if available
        if accidents_collection is not None:
            try:
                if accidents_collection.count_documents({}) == 0:
                    accidents_collection.insert_many(sample_accidents)
                    print("✅ Seeded sample accidents to MongoDB")
                return
            except Exception:
                pass

        # Fall back to in-memory storage
        if not accidents_db:
            accidents_db.extend(sample_accidents)
            print("✅ Seeded sample accidents to in-memory storage")
    except Exception:
        # Keep startup resilient; ignore seeding errors
        pass

seed_sample_data()

class AccidentDetector:
    def __init__(self):
        self.accident_threshold = 0.5
        self.previous_frame = None
        self.accident_detected = False
        
    def detect_accident(self, frame):
        """Detect accident using YOLOv8 and motion analysis"""
        if not COMPUTER_VISION_AVAILABLE or not YOLO_AVAILABLE or model is None:
            # Return mock data for demo purposes
            import random
            accident_score = random.uniform(0.1, 0.9)
            vehicles_detected = random.randint(0, 3)
            is_accident = accident_score > self.accident_threshold and vehicles_detected > 0
            return is_accident, accident_score, vehicles_detected, []
            
        try:
            # Convert frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run YOLOv8 detection
            results = model(rgb_frame)
            
            # Check for vehicles and potential accidents
            accident_score = 0
            vehicles_detected = 0
            boxes_info = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        
                        # Check for vehicles (car, truck, bus, motorcycle)
                        if class_id in [2, 3, 5, 7] and confidence > 0.3:
                            vehicles_detected += 1
                            # Collect bounding box for frontend overlay
                            try:
                                x1, y1, x2, y2 = box.xyxy[0].tolist()
                                boxes_info.append({
                                    'x1': float(x1), 'y1': float(y1), 'x2': float(x2), 'y2': float(y2),
                                    'class_id': class_id, 'confidence': confidence
                                })
                            except Exception:
                                pass
                            
                            # Simple motion detection for accident
                            if self.previous_frame is not None:
                                gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                gray_previous = cv2.cvtColor(self.previous_frame, cv2.COLOR_BGR2GRAY)
                                
                                # Calculate frame difference
                                frame_diff = cv2.absdiff(gray_current, gray_previous)
                                motion_score = np.mean(frame_diff) / 255.0
                                
                                # High motion + vehicle detection = potential accident
                                if motion_score > 0.15:
                                    accident_score += confidence * motion_score
                
                # Store current frame for next comparison
                self.previous_frame = frame.copy()
                
                # Determine if accident occurred
                if accident_score > self.accident_threshold and vehicles_detected > 0:
                    if not self.accident_detected:
                        self.accident_detected = True
                        return True, accident_score, vehicles_detected, boxes_info
                else:
                    self.accident_detected = False
                    
            return False, accident_score, vehicles_detected, boxes_info
            
        except Exception as e:
            print(f"Error in accident detection: {e}")
            return False, 0, 0, []

detector = AccidentDetector()

def get_location_info(lat, lng):
    """Get location information using coordinates"""
    if not LOCATION_SERVICES_AVAILABLE:
        return f"Lat: {lat}, Lng: {lng}"
    
    try:
        geolocator = Nominatim(user_agent="accident_detection")
        location = geolocator.reverse(f"{lat}, {lng}")
        return location.address if location else f"Lat: {lat}, Lng: {lng}"
    except:
        return f"Lat: {lat}, Lng: {lng}"

def send_alert(accident_data):
    """Send alert to emergency services"""
    try:
        # Store accident data
        accident_record = {
            "timestamp": datetime.now().isoformat(),
            "location": accident_data["location"],
            "coordinates": accident_data["coordinates"],
            "confidence": accident_data["confidence"],
            "vehicles_detected": accident_data["vehicles_detected"],
            "status": "alert_sent"
        }
        
        # Store in database
        if accidents_collection is not None:
            accidents_collection.insert_one(accident_record)
        else:
            accidents_db.append(accident_record)
        
        # Send SMS alert via Twilio
        if twilio_client:
            message = f"""
            🚨 ACCIDENT DETECTED 🚨
            
            Location: {accident_data['location']}
            Coordinates: {accident_data['coordinates']['lat']}, {accident_data['coordinates']['lng']}
            Confidence: {accident_data['confidence']:.2f}
            Vehicles Detected: {accident_data['vehicles_detected']}
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Please dispatch emergency services immediately!
            """
            
            # Send to emergency contacts
            emergency_contacts = ["+1234567890", "+0987654321"]  # Add real numbers
            
            for contact in emergency_contacts:
                try:
                    twilio_client.messages.create(
                        body=message,
                        from_=TWILIO_PHONE_NUMBER,
                        to=contact
                    )
                except Exception as e:
                    print(f"Failed to send SMS to {contact}: {e}")
        
        # Store in Firebase
        if db_firestore is not None:
            db_firestore.collection('accidents').add(accident_record)
        
        subject = "ACCIDENT DETECTED"
        body = (
            "ACCIDENT DETECTED\n\n"
            f"Location: {accident_data['location']}\n"
            f"Coordinates: {accident_data['coordinates']['lat']}, {accident_data['coordinates']['lng']}\n"
            f"Confidence: {accident_data['confidence']:.2f}\n"
            f"Vehicles Detected: {accident_data['vehicles_detected']}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        send_email_alert(subject, body)

        print(f"Alert sent for accident at {accident_data['location']}")
        return True
        
    except Exception as e:
        print(f"Error sending alert: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Check user credentials
        if username in users_db and bcrypt.checkpw(password.encode('utf-8'), users_db[username]['password']):
            access_token = create_access_token(identity=username)
            return jsonify({
                'success': True,
                'access_token': access_token,
                'user': {'username': username, 'role': users_db[username].get('role', 'user')}
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if username in users_db:
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Store user
        users_db[username] = {
            'password': hashed_password,
            'email': email,
            'role': 'user',
            'created_at': datetime.now().isoformat()
        }
        
        # Store in MongoDB if available
        if users_collection is not None:
            users_collection.insert_one({
                'username': username,
                'password': hashed_password,
                'email': email,
                'role': 'user',
                'created_at': datetime.now().isoformat()
            })
        
        return jsonify({'success': True, 'message': 'User created successfully'})
    
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/detect', methods=['POST'])
@jwt_required()
def detect_accident():
    global last_alert_time
    try:
        data = request.get_json()
        image_data = data.get('image')
        # Allow UI to control detector threshold per request
        try:
            threshold = float(data.get('threshold')) if data and data.get('threshold') is not None else None
            if threshold is not None:
                detector.accident_threshold = max(0.1, min(1.0, threshold))
        except Exception:
            pass
        
        if not image_data:
            return jsonify({'error': 'No image data provided'})
        
        if not COMPUTER_VISION_AVAILABLE or not YOLO_AVAILABLE:
            # Return mock detection for demo
            import random
            is_accident = random.random() > 0.8  # 20% chance of accident
            confidence = random.uniform(0.1, 0.95)
            vehicles = random.randint(0, 3)
            boxes = []
            result = {
                'accident_detected': is_accident,
                'confidence': float(confidence),
                'vehicles_detected': vehicles,
                'boxes': boxes,
                'timestamp': datetime.now().isoformat(),
                'demo_mode': True
            }
            
            if is_accident:
                now = time.time()
                if now - last_alert_time >= ALERT_COOLDOWN_SECONDS:
                    last_alert_time = now
                    accident_data = {
                        'location': get_location_info(current_location['lat'], current_location['lng']),
                        'coordinates': current_location,
                        'confidence': confidence,
                        'vehicles_detected': vehicles
                    }
                    send_alert(accident_data)
                    result['alert_sent'] = True
                    result['alert_suppressed'] = False
                else:
                    result['alert_sent'] = False
                    result['alert_suppressed'] = True
            else:
                result['alert_suppressed'] = False
            
            return jsonify(result)
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detect accident
        is_accident, confidence, vehicles, boxes = detector.detect_accident(frame)
        
        result = {
            'accident_detected': is_accident,
            'confidence': float(confidence),
            'vehicles_detected': vehicles,
            'boxes': boxes,
            'timestamp': datetime.now().isoformat()
        }
        
        # If accident detected, send alert
        if is_accident:
            now = time.time()
            if now - last_alert_time >= ALERT_COOLDOWN_SECONDS:
                last_alert_time = now
                accident_data = {
                    'location': get_location_info(current_location['lat'], current_location['lng']),
                    'coordinates': current_location,
                    'confidence': confidence,
                    'vehicles_detected': vehicles
                }
                send_alert(accident_data)
                result['alert_sent'] = True
                result['alert_suppressed'] = False
            else:
                result['alert_sent'] = False
                result['alert_suppressed'] = True
        else:
            result['alert_suppressed'] = False
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/update_location', methods=['POST'])
@jwt_required()
def update_location():
    global current_location
    data = request.get_json()
    current_location = {
        'lat': float(data.get('lat', 28.6139)),
        'lng': float(data.get('lng', 77.2090))
    }
    return jsonify({'success': True, 'location': current_location})

@app.route('/accidents', methods=['GET'])
@jwt_required()
def get_accidents():
    try:
        if accidents_collection is not None:
            accidents = list(accidents_collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(50))
        else:
            accidents = sorted(accidents_db, key=lambda x: x['timestamp'], reverse=True)[:50]
        
        return jsonify({'accidents': accidents})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/camera_feed')
def camera_feed():
    return render_template('camera.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

