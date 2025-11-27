import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")

try:
    import google.generativeai
    print("SUCCESS: google.generativeai imported")
    print(f"Location: {google.generativeai.__file__}")
except ImportError as e:
    print(f"ERROR: {e}")
except Exception as e:
    print(f"ERROR: {e}")
