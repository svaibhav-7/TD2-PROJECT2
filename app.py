"""
Main Flask application for LLM Analysis Quiz Solver
Handles API endpoints and orchestrates quiz solving
"""

import os
from dotenv import load_dotenv
import config
import json
import time
import logging
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional, Tuple
import asyncio
import threading
from datetime import datetime

from quiz_solver import QuizSolver
from data_processor import DataProcessor

import sys

# Configure logging to console and file
logging.basicConfig(
    filename=config.LOG_FILE,
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Add file handler so we can tail logs
file_handler = logging.FileHandler(config.LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
file_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
logger.addHandler(file_handler)

app = Flask(__name__)

# Load environment from .env (so SECRET_KEY / EMAIL set from .env when running locally)
load_dotenv()

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-here')
EMAIL = os.getenv('EMAIL', 'your-email@example.com')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize components
quiz_solver = QuizSolver(openai_api_key=OPENAI_API_KEY or '')
data_processor = DataProcessor()

# Track submission times for 3-minute window
submission_tracker: Dict[str, float] = {}
SUBMISSION_TIMEOUT = 180  # 3 minutes in seconds


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'email': EMAIL
    }), 200


@app.route('/quiz', methods=['POST'])
def handle_quiz():
    """
    Main endpoint to receive quiz requests
    
    Expected JSON:
    {
        "email": "student@example.com",
        "secret": "secret-string",
        "url": "https://example.com/quiz-123"
    }
    
    Response:
    {
        "status": "processing" | "error",
        "submission_id": "...",
        "message": "..."
    }
    """
    
    # Validate request format
    try:
        # silent=True prevents 415 error if Content-Type is not application/json
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({'error': 'Invalid JSON or Content-Type'}), 400
    except Exception as e:
        logger.error(f"JSON parsing error: {e}")
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # Extract fields
    email = data.get('email')
    secret = data.get('secret')
    quiz_url = data.get('url')
    
    # Validate required fields
    if not all([email, secret, quiz_url]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify secret
    if secret != SECRET_KEY:
        logger.warning(f"Invalid secret attempt from {email}")
        return jsonify({'error': 'Invalid secret'}), 403
    
    # Verify email matches
    if email != EMAIL:
        logger.warning(f"Email mismatch: {email} != {EMAIL}")
        return jsonify({'error': 'Email mismatch'}), 403
    
    # Record submission start time
    submission_id = f"{quiz_url}_{int(time.time())}"
    submission_tracker[submission_id] = time.time()
    
    logger.info(f"Received quiz request: {quiz_url}")
    
    # Start quiz solving in background thread so we can return immediately
    def _runner(url: str, sid: str):
        try:
            asyncio.run(solve_quiz_sequence(url, sid))
        except Exception as e:
            logger.error(f"Background solver error for {sid}: {e}", exc_info=True)

    try:
        thread = threading.Thread(target=_runner, args=(quiz_url, submission_id), daemon=True)
        thread.start()
        return jsonify({
            'status': 'success',
            'submission_id': submission_id,
            'message': 'Quiz solving initiated'
        }), 200
    except Exception as e:
        logger.error(f"Error starting background solver: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


async def solve_quiz_sequence(initial_url: str, submission_id: str) -> Dict[str, Any]:
    """
    Solve a sequence of quiz questions
    
    Handles:
    - Visiting quiz URL
    - Extracting question
    - Processing data
    - Submitting answer
    - Following chain of URLs if provided
    """
    current_url = initial_url
    attempt_count = 0
    max_attempts = 10
    start_time = time.time()
    
    while current_url and attempt_count < max_attempts:
        # Check 3-minute timeout
        elapsed = time.time() - start_time
        if elapsed > SUBMISSION_TIMEOUT:
            logger.warning(f"Timeout exceeded for {submission_id}")
            break
        
        try:
            logger.info(f"Solving quiz at: {current_url}")
            
            # Visit quiz page and extract question
            question_data = await quiz_solver.visit_and_extract(current_url)
            logger.info(f"Extracted question: {question_data.get('question', '')[:100]}")
            
            # Process data and get answer
            answer = await process_question(question_data)
            logger.info(f"Generated answer: {answer}")
            
            # Submit answer
            submit_url = question_data.get('submit_url', question_data.get('url'))
            logger.info(f"Using submit_url from question_data: {question_data.get('submit_url')} (resolved submit_url: {submit_url})")
            response = await quiz_solver.submit_answer(
                url=submit_url,
                answer=answer,
                quiz_url=current_url,
                email=EMAIL,
                secret=SECRET_KEY
            )
            
            logger.info(f"Submission response: {response}")
            
            # Check if correct
            if response.get('correct'):
                logger.info(f"Answer correct! Moving to next question.")
                current_url = response.get('url')  # May be None if quiz ended
                if not current_url:
                    logger.info(f"Quiz completed successfully!")
                    break
            else:
                # Try next URL if provided, otherwise re-attempt
                if response.get('url'):
                    logger.info(f"Answer incorrect. Moving to suggested URL: {response.get('url')}")
                    current_url = response.get('url')
                else:
                    logger.info(f"Answer incorrect. Reason: {response.get('reason')}")
                    # Could implement retry logic here
                    break
            
            attempt_count += 1
            
        except Exception as e:
            logger.error(f"Error solving quiz at {current_url}: {e}", exc_info=True)
            break
    
    return {
        'submission_id': submission_id,
        'attempts': attempt_count,
        'status': 'completed'
    }


async def process_question(question_data: Dict[str, Any]) -> Any:
    """
    Process a quiz question and generate answer
    
    Handles:
    - Web scraping
    - PDF/data file processing
    - Statistical analysis
    - Data transformation
    - Visualization
    """
    question = question_data.get('question', '')
    
    logger.info(f"Processing question: {question}")
    
    # Attempt to parse heuristic demo metadata (submit_url or example answer) but do not skip LLM by default
    heur_result = None
    try:
        heur_result = await quiz_solver.heuristic_parse_demo(question_data)
        logger.info(f"Heuristic parse result: {heur_result}")
        if heur_result and heur_result.get('submit_url'):
            # If heuristic parse found a submit_url, use it rather than the page URL
            question_data['submit_url'] = heur_result.get('submit_url')
            logger.info(f"Heuristic detected submit_url: {heur_result.get('submit_url')}")
    except Exception as e:
        logger.debug(f"Heuristic demo parse error: {e}")

    # Use LLM to determine question type and approach
    logger.info(f"LLM primary model: {config.PRIMARY_MODEL}, fallback: {config.FALLBACK_MODEL}")
    question_type = await quiz_solver.classify_question(question)
    logger.info(f"Question type (LLM): {question_type}")
    logger.info(f"Question type: {question_type}")
    
    # Process based on question type
    if 'download' in question.lower() or 'file' in question.lower():
        answer = await handle_file_processing(question_data)
    elif 'scrape' in question.lower() or 'website' in question.lower():
        answer = await handle_web_scraping(question_data)
    elif 'api' in question.lower():
        answer = await handle_api_request(question_data)
    else:
        # Use LLM for complex analysis
        logger.info("Calling LLM for analysis")
        answer = await quiz_solver.analyze_with_llm(question, question_data)
        # If LLM generated answer, mark source
        if answer is not None:
            logger.info("Answer source: LLM")
        else:
            # LLM failed to generate an answer. Use heuristic fallback only if enabled.
            if getattr(config, 'ENABLE_HEURISTIC_FALLBACK', True):
                logger.warning(f"LLM analysis failed; last error: {quiz_solver.last_llm_error}. Attempting heuristic fallback.")
                # When grading mode is enabled, do not use heuristic answers
                if getattr(config, 'GRADING_MODE', False):
                    logger.info("GRADING_MODE=True; not using heuristic answer fallback for grading.")
                    answer = None
                else:
                    # If heur_result contains a sample answer, use that first
                    if heur_result and heur_result.get('answer') is not None:
                        logger.info("Using heuristic parsed example answer as fallback")
                        answer = heur_result.get('answer')
                        logger.info("Answer source: heuristic")
                    else:
                        answer = await quiz_solver.heuristic_solve(question_data)
                        logger.info("Answer source: heuristic")
            else:
                logger.info("Heuristic fallback disabled; not attempting heuristic fallback")
    
    return answer


async def handle_file_processing(question_data: Dict[str, Any]) -> Any:
    """Handle questions involving file downloads and processing"""
    logger.info("Handling file processing question")
    try:
        import aiohttp
        import tempfile
        import os
        from pathlib import Path
        
        question = question_data.get('question', '')
        content = question_data.get('content', '')
        
        # Use LLM to extract file URL and question from the content
        file_url = await quiz_solver.analyze_with_llm(
            f"Extract ONLY the file download URL from this text. Return just the URL, nothing else: {content}",
            {}
        )
        
        if not file_url or not isinstance(file_url, str) or not file_url.startswith('http'):
            logger.error(f"Could not extract valid URL: {file_url}")
            return None
            
        logger.info(f"Downloading file from: {file_url}")
        
        # Download the file
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to download file: {resp.status}")
                    return None
                    
                file_content = await resp.read()
        
        # Determine file type and process accordingly
        file_ext = Path(file_url).suffix.lower()
        
        if file_ext == '.pdf':
            # Save to temp file and extract
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            
            text = data_processor.extract_from_pdf(tmp_path)
            os.unlink(tmp_path)
            
            # Use LLM to answer question based on extracted text
            answer = await quiz_solver.analyze_with_llm(
                f"Based on this text, answer: {question}",
                {'extracted_text': text[:5000]}  # Limit to avoid token limits
            )
            
        elif file_ext in ['.csv', '.txt']:
            # Process CSV
            df = data_processor.process_csv(file_content)
            if df is not None:
                # Use LLM to determine what operation to perform
                operation = await quiz_solver.analyze_with_llm(
                    f"What data operation is needed? Question: {question}. Columns: {list(df.columns)}",
                    {}
                )
                
                # Try common operations
                if 'sum' in question.lower():
                    # Find the column to sum
                    for col in df.columns:
                        if 'value' in col.lower() or 'amount' in col.lower() or 'total' in col.lower():
                            answer = data_processor.sum_column(df, col)
                            break
                elif 'count' in question.lower():
                    answer = data_processor.count_rows(df)
                else:
                    # Let LLM analyze the data
                    answer = await quiz_solver.analyze_with_llm(
                        question,
                        {'data_summary': df.describe().to_dict(), 'columns': list(df.columns)}
                    )
            else:
                answer = None
                
        elif file_ext in ['.json']:
            json_data = data_processor.process_json(file_content.decode('utf-8'))
            answer = await quiz_solver.analyze_with_llm(
                question,
                {'data': json_data}
            )
            
        else:
            logger.warning(f"Unsupported file type: {file_ext}")
            answer = None
            
        return answer
        
    except Exception as e:
        logger.error(f"Error in file processing: {e}", exc_info=True)
        return None


async def handle_web_scraping(question_data: Dict[str, Any]) -> Any:
    """Handle questions involving web scraping"""
    logger.info("Handling web scraping question")
    
    try:
        question = question_data.get('question', '')
        content = question_data.get('content', '')
        
        # Extract URL to scrape from question
        url_to_scrape = await quiz_solver.analyze_with_llm(
            f"Extract ONLY the URL to scrape from this text. Return just the URL: {content}",
            {}
        )
        
        if not url_to_scrape or not isinstance(url_to_scrape, str) or not url_to_scrape.startswith('http'):
            logger.error(f"Could not extract URL to scrape: {url_to_scrape}")
            return None
        
        logger.info(f"Scraping URL: {url_to_scrape}")
        
        # Use Playwright to scrape
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url_to_scrape, wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            # Get page content
            scraped_content = await page.content()
            text_content = await page.text_content('body')
            
            await browser.close()
        
        # Use LLM to extract answer from scraped content
        answer = await quiz_solver.analyze_with_llm(
            f"Based on this scraped content, answer: {question}",
            {'scraped_text': text_content[:5000] if text_content else scraped_content[:5000]}
        )
        
        return answer
        
    except Exception as e:
        logger.error(f"Error in web scraping: {e}", exc_info=True)
        return None


async def handle_api_request(question_data: Dict[str, Any]) -> Any:
    """Handle questions involving API requests"""
    logger.info("Handling API request question")
    
    try:
        import aiohttp
        
        question = question_data.get('question', '')
        content = question_data.get('content', '')
        
        # Use LLM to extract API endpoint and any headers
        api_info = await quiz_solver.analyze_with_llm(
            f"Extract API endpoint URL and any required headers from: {content}. Format as JSON with 'url' and 'headers' keys.",
            {}
        )
        
        # Try to parse as JSON
        import json
        if isinstance(api_info, str):
            try:
                api_info = json.loads(api_info)
            except:
                # If not JSON, assume it's just the URL
                api_info = {'url': api_info, 'headers': {}}
        
        api_url = api_info.get('url', '') if isinstance(api_info, dict) else str(api_info)
        api_headers = api_info.get('headers', {}) if isinstance(api_info, dict) else {}
        
        if not api_url or not api_url.startswith('http'):
            logger.error(f"Could not extract valid API URL: {api_url}")
            return None
        
        logger.info(f"Calling API: {api_url}")
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=api_headers) as resp:
                if resp.status != 200:
                    logger.error(f"API request failed: {resp.status}")
                    return None
                
                api_response = await resp.json()
        
        # Use LLM to analyze API response and answer question
        answer = await quiz_solver.analyze_with_llm(
            f"Based on this API response, answer: {question}",
            {'api_response': api_response}
        )
        
        return answer
        
    except Exception as e:
        logger.error(f"Error in API request: {e}", exc_info=True)
        return None


if __name__ == '__main__':
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        threaded=True
    )
