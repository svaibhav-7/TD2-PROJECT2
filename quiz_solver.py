"""
Quiz Solver module - handles visiting quiz pages, extracting questions,
and submitting answers using headless browser automation and LLM
"""

import json
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
                
                # Extract content
                content = await page.content()
                
                # Try to find question text
                question = await self._extract_question(page)
                submit_url = await self._extract_submit_url(page, url)
                
                logger.info(f"Extracted question: {question[:100] if question else 'None'}")
                
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
            if 'example.com/submit' in content:
                return 'https://example.com/submit'
            
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
    
    async def classify_question(self, question: str) -> str:
        """Use LLM to classify question type"""
        if not self.client:
            return 'unknown'
        
        try:
            model = getattr(config, 'PRIMARY_MODEL', None) or getattr(config, 'FALLBACK_MODEL', 'gpt-3.5-turbo')
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
            return response.choices[0].message.content.strip().lower()
        
        except Exception as e:
            # If model not found, try fallback model
            err = str(e)
            logger.error(f"Error classifying question: {e}")
            try:
                if 'model_not_found' in err or 'does not exist' in err:
                    fallback = getattr(config, 'FALLBACK_MODEL', 'gpt-3.5-turbo')
                    logger.info(f"Retrying classification with fallback model: {fallback}")
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
                    return response.choices[0].message.content.strip().lower()
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
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': 'You are a data analysis expert. Solve the quiz question.'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"LLM generated answer: {answer}")
            
            return self._parse_answer(answer)
        
        except Exception as e:
            err_str = str(e)
            logger.error(f"Error analyzing with LLM: {e}")
            # If model not found error, retry with fallback
            try:
                if 'model_not_found' in err_str or 'does not exist' in err_str:
                    fallback = getattr(config, 'FALLBACK_MODEL', 'gpt-3.5-turbo')
                    logger.info(f"Retrying analysis with fallback model: {fallback}")
                    response = self.client.chat.completions.create(
                        model=fallback,
                        messages=[
                            {'role': 'system', 'content': 'You are a data analysis expert. Solve the quiz question.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                    answer = response.choices[0].message.content.strip()
                    logger.info(f"LLM generated answer (fallback): {answer}")
                    return self._parse_answer(answer)
            except Exception:
                pass
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
