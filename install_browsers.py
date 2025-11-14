"""
Setup script to install Playwright browsers after pip install
Run this once after installing dependencies
"""

import subprocess
import sys

print("Installing Playwright browsers...")
print("This may take a few minutes...")
print()

try:
    result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    print("\n✅ Playwright Chromium browser installed successfully!")
except subprocess.CalledProcessError as e:
    print(f"\n❌ Error installing Playwright: {e}")
    sys.exit(1)

print("\n✅ Setup complete! You can now run:")
print("   python generate_prompts.py")
print("   python main.py")
