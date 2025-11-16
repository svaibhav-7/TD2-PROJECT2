"""
Configuration and environment setup
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'production')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# API Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-here')
EMAIL = os.getenv('EMAIL', 'your-email@example.com')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Timeout settings
SUBMISSION_TIMEOUT = 180  # 3 minutes
BROWSER_TIMEOUT = 30000  # 30 seconds

# Model configuration
PRIMARY_MODEL = 'gpt-3.5-turbo'
FALLBACK_MODEL = 'gpt-3.5-turbo'

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'quiz_solver.log')

# Database configuration (if needed)
DATABASE_URL = os.getenv('DATABASE_URL', None)

# API endpoint configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5000))

# Validate required configuration
def validate_config():
    """Validate that all required configuration is present"""
    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not set. LLM features will be limited.")
    
    if SECRET_KEY == 'your-secret-here':
        print("WARNING: Using default SECRET_KEY. Please set SECRET_KEY environment variable.")
    
    if EMAIL == 'your-email@example.com':
        print("WARNING: Using default EMAIL. Please set EMAIL environment variable.")

if __name__ == '__main__':
    validate_config()
    print("Configuration loaded successfully")
