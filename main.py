"""
Main entry point - run this to start the API server
"""

import sys
import os
from pathlib import Path
import config

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure environment
os.environ.setdefault('FLASK_ENV', 'production')

# Import and run app
from app import app, logger

if __name__ == '__main__':
    logger.info("Starting LLM Analysis Quiz Solver API")
    logger.info(f"Host: {config.API_HOST}, Port: {config.API_PORT}")
    # Use configuration variable for debug; this respects .env and config.py
    debug_flag = getattr(config, 'FLASK_DEBUG', False)
    try:
        app.run(host=config.API_HOST, port=config.API_PORT, debug=debug_flag, threaded=True)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
