"""
Test client for the API endpoint
Use this to test your implementation before submitting
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
EMAIL = os.getenv('EMAIL', 'your-email@example.com')
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
API_URL = os.getenv('API_URL', 'http://localhost:5000')
DEMO_URL = 'https://tds-llm-analysis.s-anand.net/demo'


def test_health_check():
    """Test health endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_invalid_json():
    """Test with invalid JSON"""
    print("\n" + "="*80)
    print("TEST 2: Invalid JSON (should return 400)")
    print("="*80)
    
    try:
        response = requests.post(f"{API_URL}/quiz", data="not json")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_missing_fields():
    """Test with missing required fields"""
    print("\n" + "="*80)
    print("TEST 3: Missing Fields (should return 400)")
    print("="*80)
    
    try:
        payload = {"email": EMAIL}  # Missing secret and url
        response = requests.post(f"{API_URL}/quiz", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_invalid_secret():
    """Test with invalid secret"""
    print("\n" + "="*80)
    print("TEST 4: Invalid Secret (should return 403)")
    print("="*80)
    
    try:
        payload = {
            "email": EMAIL,
            "secret": "wrong-secret",
            "url": DEMO_URL
        }
        response = requests.post(f"{API_URL}/quiz", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 403
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_valid_request():
    """Test with valid request"""
    print("\n" + "="*80)
    print("TEST 5: Valid Request (should return 200)")
    print("="*80)
    
    try:
        payload = {
            "email": EMAIL,
            "secret": SECRET_KEY,
            "url": DEMO_URL
        }
        response = requests.post(f"{API_URL}/quiz", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("█" * 80)
    print("API ENDPOINT TEST SUITE")
    print("█" * 80)
    print(f"\nConfiguration:")
    print(f"  Email: {EMAIL}")
    print(f"  Secret: {SECRET_KEY}")
    print(f"  API URL: {API_URL}")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Invalid JSON", test_invalid_json()))
    results.append(("Missing Fields", test_missing_fields()))
    results.append(("Invalid Secret", test_invalid_secret()))
    results.append(("Valid Request", test_valid_request()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for _, p in results if p)
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n✓ All tests passed! Your API is ready for evaluation.")
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")


if __name__ == '__main__':
    main()
