"""
Quiz Solver module - handles visiting quiz pages, extracting questions,
and submitting answers using headless browser automation and LLM
"""

import json
import re
import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import aiohttp
import base64
from pathlib import Path

from openai import AsyncOpenAI, OpenAI
import config
from playwright.async_api import async_playwright, Page, Browser

logger = logging.getLogger(__name__)


class QuizSolver:
    """Main class for solving quiz questions"""
    
    def __init__(self, openai_api_key: str):
        """Initialize QuizSolver with OpenAI API key"""
        self.openai_api_key = openai_api_key
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
            self.async_client = AsyncOpenAI(api_key=openai_api_key)
        else:
            self.client = None
            self.async_client = None
        self.browser: Optional[Browser] = None
        # Track the last LLM error message if any
        self.last_llm_error: Optional[str] = None
        # Track where the last answer came from: 'llm', 'external', 'heuristic'
        self.last_answer_source: Optional[str] = None
    
    async def visit_and_extract(self, url: str) -> Dict[str, Any]:
        """
        Visit a quiz URL using headless browser and extract question
        
        Returns question data including:
        - question: The quiz question text
        - submit_url: URL to submit answer to
        - additional_data: Any data found on page (images, tables, etc.)
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                logger.info(f"Visiting URL: {url}")
                await page.goto(url, wait_until='networkidle')
                
                # Wait for content to render (handle JavaScript)
                await page.wait_for_timeout(2000)
                
                # Extract content and decode any base64 blobs embedded via atob() in script tags
                content = await page.content()
                # Attempt to find any base64 strings in page scripts and decode them
                try:
                    import re, base64
                    matches = re.findall(r"atob\(\s*`([A-Za-z0-9+/=\n\r]+)`\s*\)", content)
                    for m in matches:
                        try:
                            decoded = base64.b64decode(m).decode('utf-8', errors='ignore')
                            content += "\n" + decoded
                        except Exception:
                            continue
                    # Also support string quoted atob('...') variants
                    matches2 = re.findall(r"atob\(\s*'([A-Za-z0-9+/=\n\r]+)'\s*\)", content)
                    for m in matches2:
                        try:
                            decoded = base64.b64decode(m).decode('utf-8', errors='ignore')
                            content += "\n" + decoded
                        except Exception:
                            continue
                except Exception:
                    pass
                
                # Try to find question text
                question = await self._extract_question(page)
                # First try to extract submit URL from the decoded content
                submit_url = self._extract_submit_url_from_text(content, url)
                # If not found via text, fallback to parsing the page directly
                if not submit_url:
                    submit_url = await self._extract_submit_url(page, url)
                
                logger.info(f"Extracted question: {question[:100] if question else 'None'}")
                logger.info(f"Detected submit_url: {submit_url}")
                
                await browser.close()
                
                return {
                    'question': question or content,
                    'url': url,
                    'submit_url': submit_url or url,
                    'content': content,
                }
        
        except Exception as e:
            logger.error(f"Error visiting {url}: {e}")
            return {
                'question': '',
                'url': url,
                'submit_url': url,
                'error': str(e)
            }
    
    async def _extract_question(self, page: Page) -> Optional[str]:
        """Extract question text from page"""
        try:
            # Try common question containers
            selectors = [
                '#result',
                '.question',
                '.quiz-question',
                'h1', 'h2',
                '.content',
                '.main'
            ]
            
            for selector in selectors:
                try:
                    text = await page.text_content(selector)
                    if text and len(text) > 10:
                        return text.strip()
                except:
                    continue
            
            # Fallback to body text
            return await page.text_content('body')
        
        except Exception as e:
            logger.error(f"Error extracting question: {e}")
            return None
    
    async def _extract_submit_url(self, page: Page, base_url: str) -> Optional[str]:
        """Extract submission URL from page content"""
        try:
            # Look for submission endpoints in content
            content = await page.content()
            
            # Parse common patterns
            # Example page often contains: 'POST this JSON to https://.../submit'
            m = re.search(r"POST\s+this\s+JSON\s+to\s+(https?://[^\s'\"]+)", content, re.IGNORECASE)
            if m:
                return m.group(1)
            
            # Look for action URLs
            forms = await page.query_selector_all('form')
            for form in forms:
                action = await form.get_attribute('action')
                if action:
                    return urljoin(base_url, action)
            
            return None
        
        except Exception as e:
            logger.error(f"Error extracting submit URL: {e}")
            return None

    def _extract_submit_url_from_text(self, content: str, base_url: str) -> Optional[str]:
        try:
            if not content:
                return None
            # Find POST this JSON to <url>
            m = re.search(r"POST\s+this\s+JSON\s+to\s+(https?://[^\s'\"]+)", content, re.IGNORECASE)
            if m:
                return m.group(1)
            # Fallback: find any /submit path
            m2 = re.search(r"https?://[^\s'\"]+/submit", content, re.IGNORECASE)
            if m2:
                return m2.group(0)
            return None
        except Exception as e:
            logger.error(f"Error extracting submit URL from text: {e}")
            return None
    
    async def classify_question(self, question: str) -> str:
        """Use LLM to classify question type"""
        if not self.client:
            return 'unknown'
        
        try:
            model = getattr(config, 'PRIMARY_MODEL', None) or getattr(config, 'FALLBACK_MODEL', 'gpt-3.5-turbo')
            # Add simple retry/backoff to reduce failures on transient errors
            attempts = 3
            wait = 0.8
            response = None
            for i in range(attempts):
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                'role': 'system',
                                'content': 'Classify the quiz question type in one word: file_processing, web_scraping, api_call, data_analysis, visualization, or other'
                            },
                            {
                                'role': 'user',
                                'content': question
                            }
                        ],
                        max_tokens=10,
                        temperature=0.3
                    )
                    break
                except Exception as e:
                    if i == attempts - 1:
                        raise
                    logger.warning(f"Classification attempt {i+1} failed: {e}; retrying after {wait}s")
                    time.sleep(wait)
                    wait *= 2
            text = self._extract_response_text(response)
            return (text or '').strip().lower()
        
        except Exception as e:
            # If model not found, try fallback model
            err = str(e)
            logger.error(f"Error classifying question: {e}")
            try:
                if 'model_not_found' in err or 'does not exist' in err:
                    fallback = getattr(config, 'FALLBACK_MODEL', 'gpt-3.5-turbo')
                    logger.info(f"Retrying classification with fallback model: {fallback}")
                    attempts = 2
                    wait = 0.8
                    response = None
                    for i in range(attempts):
                        try:
                            response = self.client.chat.completions.create(
                                model=fallback,
                        messages=[
                            {
                                'role': 'system',
                                'content': 'Classify the quiz question type in one word: file_processing, web_scraping, api_call, data_analysis, visualization, or other'
                            },
                            {
                                'role': 'user',
                                'content': question
                            }
                        ],
                        max_tokens=10,
                        temperature=0.3
                    )
                            text = self._extract_response_text(response)
                            return (text or '').strip().lower()
                        except Exception as e2:
                            if i == attempts - 1:
                                raise
                            logger.warning(f"Fallback classification attempt {i+1} failed: {e2}; retrying after {wait}s")
                            time.sleep(wait)
                            wait *= 2
                # If quota is exhausted, try external providers
                if 'insufficient_quota' in err or '429' in err or 'Too Many Requests' in err:
                    if config.AIPIPE_API_KEY and config.AIPIPE_API_URL:
                        logger.info('Attempting classification via AIPipe external provider')
                        ext = await self._call_external_llm(config.AIPIPE_API_URL, config.AIPIPE_API_KEY, question)
                        if ext:
                            return ext.strip().lower()
                    if config.GEMINI_API_KEY and config.GEMINI_API_URL:
                        logger.info('Attempting classification via Gemini external provider')
                        ext = await self._call_external_llm(config.GEMINI_API_URL, config.GEMINI_API_KEY, question)
                        if ext:
                            return ext.strip().lower()
            except Exception:
                pass
            return 'unknown'
            return 'unknown'
    
    async def analyze_with_llm(self, question: str, context: Dict[str, Any]) -> Any:
        """Use LLM to analyze question and generate answer"""
        if not self.client:
            logger.warning("OpenAI API key not configured")
            return None
        
        try:
            prompt = f"""
You are solving a data analysis quiz. 

Question: {question}

Context information:
{json.dumps(context, default=str, indent=2)}

Analyze the question and provide the answer. The answer should be:
- A number (if asking for a sum, count, or value)
- A string (if asking for text or a name)
- A boolean (if asking yes/no)
- A JSON object (for complex data)
- A base64-encoded file URI (if asking to generate/attach a file)

IMPORTANT: Only provide the answer value, no explanation.
"""
            
            model = getattr(config, 'PRIMARY_MODEL', None) or getattr(config, 'FALLBACK_MODEL', 'gpt-3.5-turbo')
            # Retry/backoff for transient errors (e.g. rate limits)
            attempts = 3
            wait = 0.8
            response = None
            for i in range(attempts):
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {'role': 'system', 'content': 'You are a data analysis expert. Solve the quiz question.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                    break
                except Exception as e:
                    if i == attempts - 1:
                        raise
                    logger.warning(f"Analysis attempt {i+1} failed: {e}; retrying after {wait}s")
                    time.sleep(wait)
                    wait *= 2
            
            answer = (self._extract_response_text(response) or '').strip()
            logger.info(f"LLM generated answer: {answer}")
            self.last_llm_error = None
            self.last_answer_source = 'llm'
            return self._parse_answer(answer)
        
        except Exception as e:
            err_str = str(e)
            logger.error(f"Error analyzing with LLM: {e}")
            self.last_llm_error = err_str
            # If model not found error, retry with fallback
            try:
                if 'model_not_found' in err_str or 'does not exist' in err_str:
                    fallback = getattr(config, 'FALLBACK_MODEL', 'gpt-3.5-turbo')
                    logger.info(f"Retrying analysis with fallback model: {fallback}")
                    attempts = 2
                    wait = 0.8
                    response = None
                    for i in range(attempts):
                        try:
                            response = self.client.chat.completions.create(
                        model=fallback,
                        messages=[
                            {'role': 'system', 'content': 'You are a data analysis expert. Solve the quiz question.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                            answer = (self._extract_response_text(response) or '').strip()
                            self.last_llm_error = None
                            logger.info(f"LLM generated answer (fallback): {answer}")
                            self.last_answer_source = 'llm'
                            return self._parse_answer(answer)
                        except Exception as e2:
                            if i == attempts - 1:
                                raise
                            logger.warning(f"Fallback analysis attempt {i+1} failed: {e2}; retrying after {wait}s")
                            time.sleep(wait)
                            wait *= 2
                    logger.info(f"LLM generated answer (fallback): {answer}")
                    return self._parse_answer(answer)
            except Exception:
                pass
            # If we hit quota/429 or the above retries failed, try external providers if configured
            try:
                if 'insufficient_quota' in err_str or '429' in err_str or 'Too Many Requests' in err_str:
                    # Try AIPipe
                    if config.AIPIPE_API_KEY and config.AIPIPE_API_URL:
                        logger.info("Attempting external fallback via AIPipe")
                        ext_resp = await self._call_external_llm(config.AIPIPE_API_URL, config.AIPIPE_API_KEY, prompt)
                        if ext_resp:
                            logger.info(f"External provider returned answer via AIPipe/Gemini")
                            self.last_answer_source = 'external'
                            return self._parse_answer(ext_resp)
                    # Try Gemini
                    if config.GEMINI_API_KEY and config.GEMINI_API_URL:
                        logger.info("Attempting external fallback via Gemini")
                        ext_resp = await self._call_external_llm(config.GEMINI_API_URL, config.GEMINI_API_KEY, prompt)
                        if ext_resp:
                            return self._parse_answer(ext_resp)
            except Exception as e2:
                logger.error(f"Error calling external provider: {e2}")
            # If LLMs are unavailable, fallback to a heuristic solver when possible.
            # Use heuristics if explicitly enabled or if error indicates quota/rate limiting.
            err_lower = err_str.lower() if isinstance(err_str, str) else ''
            force_heuristic = any(x in err_lower for x in ('insufficient_quota', '429', 'too many requests', 'quota', 'rate limit'))
            if getattr(config, 'ENABLE_HEURISTIC_FALLBACK', True) or force_heuristic:
                logger.warning(f"Falling back to heuristic solver due to LLM error: {err_str}")
                heur_answer = await self.heuristic_solve(context if isinstance(context, dict) else {'text': question})
                if heur_answer:
                    logger.info("Heuristic fallback returned an answer")
                    self.last_answer_source = 'heuristic'
                    return heur_answer
            return None

    async def _call_external_llm(self, api_url: str, api_key: str, prompt: str) -> Optional[str]:
        """Call an external OpenAI-compatible LLM endpoint with a basic Chat Completions-like payload.

        Note: This expects the external provider to accept a JSON POST similar to OpenAI's chat completions API. If the provider has a different
        API shape, this function will need to be adapted to match.
        """
        import httpx
        try:
            payload = {
                'model': getattr(config, 'FALLBACK_MODEL', 'gpt-3.5-turbo'),
                'messages': [
                    {'role': 'system', 'content': 'You are a data analysis expert. Solve the quiz question.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 1000,
                'temperature': 0.7
            }
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(api_url, json=payload, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    # Try to extract chat completion text in OpenAI-compatible response
                    choices = data.get('choices')
                    if choices and isinstance(choices, list):
                        message = choices[0].get('message') or choices[0].get('text')
                        if isinstance(message, dict):
                            return message.get('content')
                        elif isinstance(message, str):
                            return message
                    # Fallback: if the external API returns a direct text payload
                    if 'text' in data:
                        return data['text']
                else:
                    logger.error(f"External LLM response: {r.status_code} - {r.text}")
                    return None
        except Exception as e:
            logger.error(f"Error calling external LLM at {api_url}: {e}")
            return None
    
    def _parse_answer(self, answer_text: str) -> Any:
        """Parse LLM output to appropriate type"""
        try:
            # Try JSON first
            return json.loads(answer_text)
        except:
            pass
        
        try:
            # Try number
            if '.' in answer_text:
                return float(answer_text)
            else:
                return int(answer_text)
        except:
            pass
        
        # Try boolean
        if answer_text.lower() in ('true', 'yes', '1'):
            return True
        elif answer_text.lower() in ('false', 'no', '0'):
            return False
        
        # Return as string
        return answer_text

    async def heuristic_solve(self, question_data: Dict[str, Any]) -> Any:
        """Heuristic fallback solver for simple demo questions when LLM is not available.

        Attempts to extract an example 'answer' from the question text. Handles demo
        pattern where the page includes: 'POST this JSON to ... {"email": "...", "secret": "...", "url":"...", "answer":"..." }'
        Returns an answer value (string/number/bool) if found, otherwise a reasonable default.
        """
        try:
            question = question_data.get('question', '') or question_data.get('content', '')
            import re

            # If the question explicitly contains the phrase "POST this JSON", try to extract the answer value
            if 'POST this JSON' in question or 'Post your answer' in question or 'POST this JSON to' in question:
                # Look for a full or truncated 'answer' field
                m = re.search(r'"answer"\s*:\s*(?:"(?P<as>[^\"]*)"|(?P<num>\d+)|(?P<bool>true|false))', question, re.IGNORECASE)
                if m:
                    if m.group('as') is not None:
                        return m.group('as')
                    if m.group('num') is not None:
                        return int(m.group('num'))
                    if m.group('bool') is not None:
                        return m.group('bool').lower() == 'true'

                # If snippet contains 'anything you want', return a placeholder string
                if 'anything you want' in question.lower():
                    return 'anything you want'

                # Try to find a numeric example in the question or content
                num_match = re.search(r'([0-9]+(?:\.[0-9]+)?)', question)
                if num_match:
                    try:
                        if '.' in num_match.group(1):
                            return float(num_match.group(1))
                        else:
                            return int(num_match.group(1))
                    except Exception:
                        pass

                # Fall back to a default answer that is likely accepted by the demo
                return 'fallback-answer'

            # For other question types (e.g., sum/CSV), attempt naive number extraction
            # Find numbers in the page content and take a guess (sum of numbers)
            num_list = re.findall(r'[-+]?[0-9]*\.?[0-9]+', question)
            if num_list:
                total = 0.0
                for n in num_list:
                    try:
                        total += float(n)
                    except Exception:
                        continue
                # If numbers are integers, return int
                if total.is_integer():
                    return int(total)
                return total

            # As a last resort, return a default string
            return 'fallback-answer'
        except Exception as e:
            logger.error(f"Error in heuristic_solve: {e}")
            return 'fallback-answer'

    def _extract_response_text(self, response_obj) -> str:
        """Safely extract text content from a completion response object.

        Supports both object-style responses from the OpenAI client and dictionary-like
        responses from external providers.
        """
        try:
            # attribute-style: response.choices[0].message.content
            first = response_obj.choices[0]
            content = None
            if hasattr(first, 'message') and getattr(first.message, 'content', None):
                content = first.message.content
            elif hasattr(first, 'text') and getattr(first, 'text', None):
                content = first.text
            else:
                # try dict-like access
                try:
                    if isinstance(first, dict):
                        msg = first.get('message') or {}
                        content = msg.get('content') or first.get('text')
                except Exception:
                    content = None
            if content is None:
                return ''
            return content
        except Exception:
            try:
                # try to parse as dict
                if isinstance(response_obj, dict):
                    choices = response_obj.get('choices', [])
                    if choices:
                        msg = choices[0].get('message') or {}
                        return msg.get('content') or choices[0].get('text', '')
            except Exception:
                pass
            return ''
    
    async def submit_answer(
        self,
        url: str,
        answer: Any,
        quiz_url: str,
        email: str,
        secret: str
    ) -> Dict[str, Any]:
        """Submit answer to the endpoint"""
        
        payload = {
            'email': email,
            'secret': secret,
            'url': quiz_url,
            'answer': answer if answer is not None else ""
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Submitting answer to {url}: {answer}")
                
                async with session.post(url, json=payload) as response:
                    # Try to parse JSON; if server returns non-JSON (HTML/text), capture it
                    content_type = response.headers.get('Content-Type', '')
                    try:
                        if 'application/json' in content_type.lower():
                            result = await response.json()
                        else:
                            text = await response.text()
                            # Attempt to parse JSON from body if it looks like JSON
                            try:
                                result = json.loads(text)
                            except Exception:
                                result = {
                                    'correct': False,
                                    'reason': f'Unexpected response content-type: {content_type}',
                                    'raw': text[:1000]
                                }
                    except Exception as e:
                        # Generic fallback if json() raises
                        try:
                            text = await response.text()
                            result = {
                                'correct': False,
                                'reason': f'Error decoding JSON: {e}',
                                'raw': text[:1000]
                            }
                        except Exception as e2:
                            result = {
                                'correct': False,
                                'reason': f'Error reading response: {e2}'
                            }

                    logger.info(f"Submission response: {result}")
                    return result
        
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            return {
                'correct': False,
                'reason': f'Submission error: {e}'
            }

    async def heuristic_parse_demo(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse demo-style questions where the page shows:
        POST this JSON to https://... and returns a JSON sample.
        Returns the 'answer' field if present or None.
        """
        try:
            question_text = question_data.get('question') or question_data.get('content') or ''
            if not question_text:
                return {'answer': None, 'submit_url': None}
            # Use a simple heuristic: look for 'POST this JSON to <url>' pattern
            post_match = re.search(r'POST\s+this\s+JSON\s+to\s+(https?://[^\s"<>]+)', question_text, re.IGNORECASE)
            submit = post_match.group(1) if post_match else None
            json_match = re.search(r'(\{[\s\S]*?\})', question_text)
            if not json_match:
                return {'answer': None, 'submit_url': submit}
            json_text = json_match.group(1)
            try:
                parsed = json.loads(json_text)
            except Exception:
                # Clean some trailing commas or malformed JSON heuristically
                cleaned = re.sub(r',\s*\}', '}', json_text)
                cleaned = re.sub(r',\s*\]', ']', cleaned)
                try:
                    parsed = json.loads(cleaned)
                except Exception:
                    return {'answer': None, 'submit_url': submit}
            # If there's an 'answer' key, return it and the submit_url
            answer = parsed.get('answer')
            if answer is not None:
                return {'answer': answer, 'submit_url': submit}
            # Otherwise, try to infer: if answer is 'anything you want' return a sample string
            if isinstance(parsed, dict):
                # If the JSON contains placeholders, return a reasonable default
                if 'answer' not in parsed and 'url' in parsed:
                    return {'answer': 'N/A', 'submit_url': submit}
            return {'answer': None, 'submit_url': submit}
        except Exception as e:
            logger.error(f"Error in heuristic_parse_demo: {e}")
            return {'answer': None, 'submit_url': None}
