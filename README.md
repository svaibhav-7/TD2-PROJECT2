# LLM Analysis Quiz Solver

An automated application that solves data analysis quizzes through web scraping, data processing, and LLM integration.

## Features

- **API Endpoint**: Accepts POST requests with quiz URLs
- **Headless Browser**: Renders JavaScript-heavy quiz pages
- **Data Processing**: Handles CSV, PDF, and web data
- **LLM Integration**: Uses GPT models for complex analysis
- **Submission System**: Automatically submits answers within 3-minute window
- **Prompt Engineering**: Secure system/user prompt pairs

## Requirements

- Python 3.10+
- OpenAI API key
- Flask/FastAPI
- Playwright (for headless browsing)
- pandas, numpy (for data analysis)

## Setup

1. Clone this repository
2. `pip install -r requirements.txt`
3. Set environment variables:
   - `OPENAI_API_KEY`
   - `SECRET_KEY` (your secret string)
   - `EMAIL` (your email)
4. Run: `python app.py`

## Project Structure

```
.
├── app.py                 # Main Flask application
├── quiz_solver.py        # Quiz solving logic
├── data_processor.py     # Data analysis utilities
├── prompt_utils.py       # Prompt engineering utilities
├── requirements.txt      # Python dependencies
└── README.md
```

## Design Choices

### System Prompt Strategy
The system prompt uses semantic obfuscation and instruction prioritization to resist code word extraction.

### User Prompt Strategy
The user prompt employs direct override techniques and explicit instructions to extract hidden information.

### API Design
RESTful endpoint with proper error handling (400 for invalid JSON, 403 for invalid secrets, 200 for success).

## License

MIT
