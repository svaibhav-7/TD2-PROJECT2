# Project Structure & File Overview

This document describes all the files created for the LLM Analysis Quiz project.

## Core Application Files

### `main.py`
- **Purpose**: Entry point for the application
- **Usage**: `python main.py` to start the API server
- **What it does**: Initializes Flask app and runs on port 5000

### `app.py`
- **Purpose**: Main Flask application with API endpoints
- **Key endpoints**:
  - `GET /health` - Health check endpoint
  - `POST /quiz` - Main quiz request handler
- **Key features**:
  - Secret verification (returns 403 if invalid)
  - JSON validation (returns 400 if invalid)
  - Async quiz solving
  - 3-minute timeout tracking

### `quiz_solver.py`
- **Purpose**: Core quiz-solving logic using headless browser and LLM
- **Key classes**: `QuizSolver`
- **Key methods**:
  - `visit_and_extract()` - Visit quiz URL with Playwright, extract question
  - `classify_question()` - Use LLM to determine question type
  - `analyze_with_llm()` - Use GPT-4 to analyze questions
  - `submit_answer()` - Submit answer back to evaluator
- **Dependencies**: Playwright, OpenAI, aiohttp

### `data_processor.py`
- **Purpose**: Data analysis and processing utilities
- **Key methods**:
  - CSV/JSON processing
  - Data aggregation, filtering, sorting
  - Statistical calculations
  - Pivot tables, correlations
  - Chart generation (matplotlib)
  - Text cleaning and number extraction
- **Dependencies**: pandas, numpy, matplotlib

### `prompt_utils.py`
- **Purpose**: Prompt engineering strategies and utilities
- **Key classes**: `PromptEngineer`
- **Strategies included**:
  - System prompts: Semantic Obfuscation, Instruction Override, Context Reset, Refusal Framework, Task Redefinition
  - User prompts: Direct Override, Creative Extraction, Jailbreak Attempt, Context Injection, Explicit Request
- **Key methods**:
  - `generate_system_prompt()` - Create defense prompt
  - `generate_user_prompt()` - Create attack prompt
  - `test_prompt_effectiveness()` - Check if code word is revealed

### `prompt_tester.py`
- **Purpose**: Test prompt effectiveness against LLM
- **Key classes**: `PromptTester`
- **Key methods**:
  - `test_system_prompt()` - Test if system prompt resists extraction
  - `test_user_prompt()` - Test if user prompt extracts code word
  - `run_comprehensive_test()` - Test multiple prompt combinations
  - `generate_test_report()` - Create test report

### `config.py`
- **Purpose**: Application configuration
- **Features**: Environment variable loading, configuration validation
- **Variables**: SECRET_KEY, EMAIL, OPENAI_API_KEY, timeouts, model names

## Utility & Setup Files

### `generate_prompts.py`
- **Purpose**: Generate and display recommended prompts for Google Form
- **Usage**: `python generate_prompts.py`
- **Output**: Shows all strategies and recommended prompts

### `test_client.py`
- **Purpose**: Test API endpoints locally
- **Usage**: `python test_client.py`
- **Tests**:
  - Health check
  - Invalid JSON (should return 400)
  - Missing fields (should return 400)
  - Invalid secret (should return 403)
  - Valid request (should return 200)

### `requirements.txt`
- **Purpose**: Python dependencies
- **Key packages**:
  - flask (web framework)
  - openai (LLM integration)
  - playwright (headless browser)
  - pandas, numpy (data processing)
  - aiohttp (async HTTP)
  - python-dotenv (environment variables)

### `.env.example`
- **Purpose**: Template for environment configuration
- **Usage**: Copy to `.env` and fill in your values
- **Variables**: EMAIL, SECRET_KEY, OPENAI_API_KEY, Flask settings

### `.env` (created after running setup)
- **Purpose**: Actual environment configuration
- **Note**: Should NOT be committed to Git (in .gitignore)

### `.gitignore`
- **Purpose**: Ignore unnecessary files in Git
- **Includes**: `.env`, `venv/`, `__pycache__/`, logs, etc.

### `setup.sh` (for Linux/Mac)
- **Purpose**: Quick setup script
- **Features**: 
  - Creates virtual environment
  - Installs dependencies
  - Installs Playwright browsers
  - Creates .env file

### `setup.bat` (for Windows)
- **Purpose**: Quick setup script for Windows
- **Features**: Same as setup.sh but for Windows PowerShell

## Documentation Files

### `README.md`
- **Purpose**: Project overview and quick start
- **Contents**:
  - Features overview
  - Requirements
  - Setup instructions
  - Project structure
  - Design choices

### `SETUP.md`
- **Purpose**: Comprehensive setup and deployment guide
- **Contents**:
  - Prerequisites
  - Step-by-step setup
  - Deployment options (Heroku, Azure, AWS, VPS)
  - Testing instructions
  - Google Form submission
  - Evaluation timeline
  - Troubleshooting

### `PROMPT_GUIDE.md`
- **Purpose**: In-depth guide on prompt engineering strategies
- **Contents**:
  - Challenge explanation
  - Scoring rules
  - 5 system prompt strategies with examples
  - 5 user prompt strategies with examples
  - Strategy recommendations
  - Testing and iteration tips
  - Common mistakes

### `SETUP.md` (this file)
- **Purpose**: You're reading it!

## License & Legal

### `LICENSE`
- **Type**: MIT License
- **Purpose**: Open source license for the project
- **Requirement**: Must be included when we evaluate

## File Statistics

- **Total files**: 19
- **Python files**: 8
- **Documentation files**: 4
- **Configuration files**: 3
- **Setup scripts**: 2
- **License**: 1

## Directory Structure

```
TD2-PROJECT2/
├── Core Application
│   ├── main.py
│   ├── app.py
│   ├── quiz_solver.py
│   ├── data_processor.py
│   ├── prompt_utils.py
│   └── prompt_tester.py
│
├── Configuration
│   ├── config.py
│   ├── .env (create from .env.example)
│   └── .env.example
│
├── Utilities
│   ├── generate_prompts.py
│   └── test_client.py
│
├── Setup
│   ├── setup.sh
│   ├── setup.bat
│   └── requirements.txt
│
├── Documentation
│   ├── README.md
│   ├── SETUP.md
│   ├── PROMPT_GUIDE.md
│   └── LICENSE
│
└── Git
    └── .gitignore
```

## Quick Start Commands

```bash
# Linux/Mac
bash setup.sh

# Windows
setup.bat

# Manually
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
python generate_prompts.py
python main.py
# In another terminal:
python test_client.py
```

## Key Workflow

1. **Setup**: Run setup script or manual commands
2. **Configure**: Edit .env with your email, secret, API key
3. **Generate Prompts**: `python generate_prompts.py`
4. **Test Locally**: `python main.py` + `python test_client.py`
5. **Deploy**: Push to GitHub, deploy to Heroku/Azure/AWS/VPS
6. **Submit**: Fill Google Form with endpoint URL and prompts
7. **Evaluate**: Endpoint receives quiz requests (Nov 29, 3-4 PM IST)
8. **Viva**: Discuss design choices

## Important Notes

- **All Python files** have logging configured
- **No sensitive data** should be in version control (use .env)
- **API must be HTTPS** (not HTTP)
- **3-minute timeout** for each quiz
- **Payload under 1 MB** size limit
- **MIT License** must be included for evaluation

## Next Steps

1. Read README.md for overview
2. Read SETUP.md for deployment guide
3. Read PROMPT_GUIDE.md for prompt strategies
4. Run setup script (setup.sh or setup.bat)
5. Generate prompts: `python generate_prompts.py`
6. Test locally: `python main.py`
7. Deploy to cloud
8. Submit Google Form
9. Prepare for viva

---

**Last Updated**: November 14, 2025
**Project**: LLM Analysis Quiz
**Status**: Ready for setup ✓
