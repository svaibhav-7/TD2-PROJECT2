"""
Main entry point - run this to start the API server
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure environment
os.environ.setdefault('FLASK_ENV', 'production')

# Import and run app
from app import app, logger

if __name__ == '__main__':
    logger.info("Starting LLM Analysis Quiz Solver API")
    logger.info(f"Host: 0.0.0.0, Port: 5000")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
