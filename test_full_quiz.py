"""
Comprehensive test of deployed endpoint with demo quiz
"""
import requests
import json
import time

EMAIL = "23f300691@ds.study.iitm.ac"
SECRET = "sasivaibhav-tdsp2-iitm"  
API_URL = "https://td2-project2.onrender.com"
DEMO_URL = "https://tds-llm-analysis.s-anand.net/demo"

print("\n" + "="*80)
print("TESTING QUIZ SOLVER WITH DEMO ENDPOINT")
print("="*80)

print(f"\n[1] Sending quiz request to: {API_URL}/quiz")
print(f"    Quiz URL: {DEMO_URL}")

payload = {
    "email": EMAIL,
    "secret": SECRET,
    "url": DEMO_URL
}

try:
    # Send quiz request
    response = requests.post(
        f"{API_URL}/quiz",
        json=payload,
        timeout=180
    )
    
    print(f"\n[2] Server Response:")
    print(f"    Status: {response.status_code}")
    print(f"    Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✓ Quiz request accepted by server")
        print("\n[3] Server is processing quiz in background...")
        print("    (The server will visit the quiz URL, solve it, and submit)")
        print("\n    Note: Check Render logs to see if the quiz was solved successfully")
        print("    The demo endpoint accepts any answer, so submission should work")
    else:
        print(f"\n✗ Quiz request failed with status {response.status_code}")
        
except requests.exceptions.Timeout:
    print("\n✗ Request timed out (>180s)")
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "="*80)
print("NEXT STEPS:")
print("="*80)
print("1. Check Render logs to verify:")
print("   - Quiz page was visited")
print("   - Question was extracted")  
print("   - LLM was called (or fallback used)")
print("   - Answer was submitted")
print("\n2. If you see errors about API keys, add them to Render environment variables:")
print("   - AIPIPE_TOKEN")
print("   - GOOGLE_API_KEY")
print("\n3. Your endpoint is HTTPS and ready for Google Form submission!")
print("="*80 + "\n")
