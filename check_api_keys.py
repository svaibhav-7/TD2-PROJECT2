"""
Check if deployed app has working LLM API keys by examining response patterns
"""
import requests
import json
import time

API_URL = "https://td2-project2.onrender.com"
EMAIL = "23f300691@ds.study.iitm.ac"
SECRET = "sasivaibhav-tdsp2-iitm"

print("\n" + "="*80)
print("DIAGNOSING LLM API KEY STATUS")
print("="*80)

print("\nSending quiz request to trigger LLM usage...")
print("This will help determine if API keys are working\n")

payload = {
    "email": EMAIL,
    "secret": SECRET,
    "url": "https://tds-llm-analysis.s-anand.net/demo"
}

response = requests.post(f"{API_URL}/quiz", json=payload)
print(f"✓ Request accepted: {response.json()}")

print("\n" + "-"*80)
print("TO CHECK IF YOUR APIs ARE WORKING:")
print("-"*80)
print("\n1. Go to Render Dashboard → Your Service → Logs")
print("\n2. Look for these log messages:")
print("   ✓ GOOD: 'Using AIPipe as primary LLM provider'")
print("   ✓ GOOD: 'Gemini configured as fallback provider'")
print("   ✗ BAD:  'Primary LLM failed (RateLimitError)...'")
print("   ✗ BAD:  'LLM analysis failed → FALLBACK used'")
print("   ✗ BAD:  'Submitting answer → ... | fallback'")

print("\n3. If you see 'fallback' being submitted:")
print("   → Go to Render Dashboard → Environment")
print("   → Add these variables:")
print("      AIPIPE_TOKEN = [your AIPipe token]")
print("      GOOGLE_API_KEY = [your Google AI Studio key]")

print("\n4. The demo endpoint accepts any answer, but REAL quizzes need correct answers!")

print("\n" + "="*80)
print("CRITICAL: Check your Render logs NOW to verify API key status")
print("="*80 + "\n")
