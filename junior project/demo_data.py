#!/usr/bin/env python3
"""
Demo data generator for AI Accident Detection System
Creates sample accident data for demonstration purposes
"""

import json
import random
from datetime import datetime, timedelta
import requests

# Sample locations in India
LOCATIONS = [
    {"name": "Delhi-Gurgaon Expressway", "lat": 28.6139, "lng": 77.2090},
    {"name": "Mumbai-Pune Expressway", "lat": 19.0760, "lng": 72.8777},
    {"name": "Bangalore-Mysore Highway", "lat": 12.9716, "lng": 77.5946},
    {"name": "Chennai-Bangalore Highway", "lat": 13.0827, "lng": 80.2707},
    {"name": "Kolkata-Durgapur Expressway", "lat": 22.5726, "lng": 88.3639},
    {"name": "Hyderabad-Vijayawada Highway", "lat": 17.3850, "lng": 78.4867},
    {"name": "Ahmedabad-Vadodara Expressway", "lat": 23.0225, "lng": 72.5714},
    {"name": "Pune-Nashik Highway", "lat": 18.5204, "lng": 73.8567}
]

def generate_demo_accidents(count=10):
    """Generate demo accident data"""
    accidents = []
    
    for i in range(count):
        # Random location
        location = random.choice(LOCATIONS)
        
        # Random time in the last 7 days
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        timestamp = datetime.now() - timedelta(
            days=days_ago, 
            hours=hours_ago, 
            minutes=minutes_ago
        )
        
        # Random accident data
        confidence = round(random.uniform(0.6, 0.95), 2)
        vehicles = random.randint(1, 4)
        
        accident = {
            "timestamp": timestamp.isoformat(),
            "location": location["name"],
            "coordinates": {
                "lat": location["lat"] + random.uniform(-0.01, 0.01),
                "lng": location["lng"] + random.uniform(-0.01, 0.01)
            },
            "confidence": confidence,
            "vehicles_detected": vehicles,
            "status": "alert_sent" if confidence > 0.8 else "detected",
            "severity": "high" if confidence > 0.9 else "medium" if confidence > 0.7 else "low"
        }
        
        accidents.append(accident)
    
    return sorted(accidents, key=lambda x: x["timestamp"], reverse=True)

def send_demo_data_to_api(accidents, base_url="http://localhost:5000"):
    """Send demo data to the API"""
    print("📡 Sending demo data to API...")
    
    try:
        # First, login to get token
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{base_url}/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                token = data.get("access_token")
                print("✅ Logged in successfully")
                
                # Send each accident
                for accident in accidents:
                    try:
                        # Update location first
                        location_response = requests.post(
                            f"{base_url}/update_location",
                            json=accident["coordinates"],
                            headers={
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {token}"
                            }
                        )
                        
                        print(f"📍 Updated location: {accident['location']}")
                        
                    except Exception as e:
                        print(f"⚠️ Could not update location: {e}")
                
                print(f"✅ Demo data prepared - {len(accidents)} accidents generated")
                return True
            else:
                print("❌ Login failed")
                return False
        else:
            print(f"❌ Login request failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure the server is running: python app.py")
        return False

def save_demo_data(accidents, filename="demo_accidents.json"):
    """Save demo data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(accidents, f, indent=2)
    print(f"💾 Demo data saved to {filename}")

def main():
    """Main function"""
    print("🎭 AI Accident Detection - Demo Data Generator")
    print("=" * 50)
    
    # Generate demo accidents
    print("📊 Generating demo accident data...")
    accidents = generate_demo_accidents(15)
    
    # Save to file
    save_demo_data(accidents)
    
    # Try to send to API
    if send_demo_data_to_api(accidents):
        print("\n🎉 Demo data setup complete!")
        print("🌐 Visit http://localhost:5000/dashboard to see the data")
    else:
        print("\n⚠️ Demo data generated but could not connect to API")
        print("💡 Start the server with 'python app.py' and run this script again")
    
    print("\n📋 Generated accidents:")
    for i, accident in enumerate(accidents[:5], 1):
        print(f"   {i}. {accident['location']} - {accident['timestamp'][:19]} - Confidence: {accident['confidence']}")

if __name__ == "__main__":
    main()
