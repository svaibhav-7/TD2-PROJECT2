"""
Test the deployed Render endpoint
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
EMAIL = os.getenv('EMAIL', '23f300691@ds.study.iitm.ac')
SECRET_KEY = os.getenv('SECRET_KEY', 'sasivaibhav-tdsp2-iitm')
API_URL = 'https://td2-project2.onrender.com'
DEMO_URL = 'https://tds-llm-analysis.s-anand.net/demo'

print("\n" + "="*80)
print("TESTING DEPLOYED RENDER ENDPOINT")
print("="*80)

# Test 1: Health check
print("\n1. Testing /health endpoint...")
try:
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("✓ Health check passed")
    else:
        print("✗ Health check failed")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: POST to /quiz
print("\n2. Testing /quiz endpoint with demo...")
try:
    payload = {
        "email": EMAIL,
        "secret": SECRET_KEY,
        "url": DEMO_URL
    }
    
    print(f"Sending: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{API_URL}/quiz", json=payload, timeout=180)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✓ Quiz request accepted")
    else:
        print("✗ Quiz request failed")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
