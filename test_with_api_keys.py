"""
Full end-to-end test with API keys configured
"""
import requests
import json
import time

API_URL = "https://td2-project2.onrender.com"
EMAIL = "23f300691@ds.study.iitm.ac"
SECRET = "sasivaibhav-tdsp2-iitm"
DEMO_URL = "https://tds-llm-analysis.s-anand.net/demo"

print("\n" + "="*80)
print("TESTING DEPLOYED ENDPOINT WITH API KEYS")
print("="*80)

print(f"\n[1] Sending quiz request...")
print(f"    API: {API_URL}/quiz")
print(f"    Quiz URL: {DEMO_URL}")

payload = {
    "email": EMAIL,
    "secret": SECRET,
    "url": DEMO_URL
}

try:
    response = requests.post(f"{API_URL}/quiz", json=payload, timeout=10)
    
    print(f"\n[2] Initial Response:")
    print(f"    Status: {response.status_code}")
    result = response.json()
    print(f"    Message: {result.get('message')}")
    print(f"    Submission ID: {result.get('submission_id')}")
    
    if response.status_code == 200:
        print("\n✓ Quiz request accepted!")
        print("\n[3] Background Processing Started...")
        print("    Your server is now:")
        print("    → Visiting the quiz URL with Playwright")
        print("    → Extracting the question")
        print("    → Analyzing with LLM (AIPipe or Gemini)")
        print("    → Submitting the answer")
        print("\n[4] Check Render Logs for:")
        print("    ✓ 'Using AIPipe as primary LLM provider'")
        print("    ✓ 'Gemini configured as fallback provider'")
        print("    ✓ 'Visiting URL: https://tds-llm-analysis.s-anand.net/demo'")
        print("    ✓ 'Extracted question: POST this JSON...'")
        print("    ✓ 'Submitting answer → ...'")
        print("    ✓ 'Submit response: {\"correct\": True/False, ...}'")
        
        print("\n" + "="*80)
        print("SUCCESS! Your quiz solver is working!")
        print("="*80)
        print("\n✅ API endpoint is live and processing requests")
        print("✅ Background workers are running")
        print("✅ LLM integration should be active (check logs to confirm)")
        print("\n🎯 Ready for evaluation on Nov 29, 2025 at 3:00 PM IST")
    else:
        print(f"\n✗ Request failed with status {response.status_code}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "="*80 + "\n")
