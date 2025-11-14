# Setup Guide - LLM Analysis Quiz

## Overview

This guide walks you through setting up and submitting your solution for the LLM Analysis Quiz project.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git
- OpenAI API key (from https://platform.openai.com/api-keys)
- A public GitHub repository

## Step 1: Clone or Create Your Repository

```bash
# If starting fresh
git init
git add .
git commit -m "Initial commit"

# Or if cloning
git clone <your-repo-url>
cd <repo-name>
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **Flask** - Web framework
- **OpenAI** - LLM integration
- **Playwright** - Headless browser automation
- **pandas/numpy** - Data processing
- **aiohttp** - Async HTTP requests
- Other utilities for PDF parsing, charting, web scraping

## Step 3: Configure Environment

Create a `.env` file by copying `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```
EMAIL=your-email@example.com
SECRET_KEY=your-secret-string-here
OPENAI_API_KEY=sk-...your-key-here...
FLASK_ENV=production
FLASK_DEBUG=False
```

## Step 4: Generate Prompts for Google Form

Run the prompt generation script to get recommended system and user prompts:

```bash
python generate_prompts.py
```

This will show you:
- Different prompt strategies
- Recommended prompts
- Character counts

## Step 5: Deploy Your API

You need to deploy your API to a publicly accessible HTTPS endpoint. Options:

### Option A: Deploy to Heroku (Free tier available)

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

heroku login
heroku create your-app-name
git push heroku main
heroku config:set EMAIL=your@email.com SECRET_KEY=your-secret OPENAI_API_KEY=sk-...
```

### Option B: Deploy to Azure

```bash
# Install Azure CLI
az webapps up --resource-group myResourceGroup --name your-app-name
```

### Option C: Deploy to AWS (Lambda + API Gateway)

Use AWS SAM or Zappa to deploy Flask to Lambda.

### Option D: Use a VPS (DigitalOcean, Linode, etc.)

```bash
# SSH into your server
ssh user@your-server.com

# Clone repo and run
git clone <your-repo-url>
cd <repo>
pip install -r requirements.txt
# Setup systemd service or use gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

**Important**: Your endpoint must be accessible via HTTPS (not HTTP).

## Step 6: Test Your API Locally

Before deployment, test locally:

```bash
# Terminal 1: Start the server
python main.py

# Terminal 2: Run tests
python test_client.py
```

You should see:
- Health check: ✓ PASSED
- Invalid JSON: ✓ PASSED (returns 400)
- Missing fields: ✓ PASSED (returns 400)
- Invalid secret: ✓ PASSED (returns 403)
- Valid request: ✓ PASSED (returns 200)

## Step 7: Fill Out the Google Form

Submit:
1. **Email**: Your email address
2. **Secret**: Your SECRET_KEY from `.env`
3. **System Prompt**: From `generate_prompts.py` output (max 100 chars)
4. **User Prompt**: From `generate_prompts.py` output (max 100 chars)
5. **API Endpoint URL**: Your deployed HTTPS URL (e.g., `https://your-app.herokuapp.com/quiz`)
6. **GitHub Repository URL**: Link to your public repo

## Step 8: Test with Demo Endpoint

After deployment, test with the demo:

```bash
curl -X POST https://your-app.herokuapp.com/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "secret": "your-secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

Expected response:
```json
{
  "status": "success",
  "submission_id": "...",
  "message": "Quiz solving initiated"
}
```

## Step 9: Prepare for Evaluation

The evaluation happens on **November 29, 2025 at 3:00 PM IST**.

Your API will receive requests with quiz URLs. You need to:

1. **Verify the secret** - Return 403 if wrong
2. **Visit the URL** with a headless browser - Extract the question
3. **Process the data** - Clean, analyze, visualize
4. **Generate answer** - Using LLM or data processing
5. **Submit answer** - Within 3 minutes

**Response format when quiz URL is received:**
```json
{
  "status": "processing",
  "submission_id": "...",
  "message": "Quiz solving initiated"
}
```

**When you submit your answer:**
```json
{
  "email": "your@email.com",
  "secret": "your-secret",
  "url": "https://example.com/quiz-834",
  "answer": 12345
}
```

## Step 10: Prepare for Viva

You'll be quizzed on:
- Why you chose that specific system prompt strategy
- How your system prompt prevents code word extraction
- Why you chose that specific user prompt strategy
- How your user prompt extracts the code word
- Your API design and architecture
- How you handle different types of data (CSV, PDF, JSON, web scraping)
- Your data processing pipeline
- How you use LLM for complex analysis

## Important Notes

### Timeout
- Quiz solving must complete within **3 minutes** of the request arriving at your server
- Only the last submission within 3 minutes counts

### Error Handling
- Return **HTTP 400** for invalid JSON
- Return **HTTP 403** for invalid secrets
- Return **HTTP 200** for valid requests (even if quiz solving fails)

### File Size
- Your answer payload must be under **1 MB**

### Multiple Attempts
- If your answer is wrong, you can re-submit within 3 minutes
- Only the last submission counts
- You may also receive a new URL to try instead

### Answer Types
- Number: `"answer": 12345`
- String: `"answer": "elephant"`
- Boolean: `"answer": true`
- JSON: `"answer": {"key": "value"}`
- Base64 file: `"answer": "data:image/png;base64,..."`

## File Structure

```
.
├── main.py                 # Entry point
├── app.py                  # Flask application
├── quiz_solver.py          # Quiz solving logic (Playwright, LLM)
├── data_processor.py       # Data analysis utilities (pandas, numpy)
├── prompt_utils.py         # Prompt engineering strategies
├── prompt_tester.py        # Test prompts
├── config.py               # Configuration
├── generate_prompts.py     # Generate prompts for form
├── test_client.py          # Test your API
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── README.md               # Project overview
├── LICENSE                 # MIT License
└── SETUP.md               # This file
```

## Troubleshooting

### "OpenAI API key not found"
- Set `OPENAI_API_KEY` in `.env` file
- Get key from https://platform.openai.com/api-keys

### "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### "Port 5000 already in use"
```bash
python main.py --port 8000
```

### API not receiving requests
- Check that your endpoint is publicly accessible
- Verify HTTPS (not HTTP)
- Check firewall settings
- Test with: `curl https://your-endpoint/health`

### Prompt length exceeds 100 characters
- Run `python generate_prompts.py` to see truncated versions
- Edit prompts manually while keeping them under 100 chars

## Next Steps

1. ✓ Install dependencies
2. ✓ Configure environment
3. ✓ Generate prompts
4. ✓ Test locally
5. ✓ Deploy to cloud
6. ✓ Fill Google Form
7. ✓ Test with demo
8. ✓ Monitor evaluation (Nov 29, 3-4 PM IST)
9. ✓ Prepare for viva

## Contact

If you have issues:
1. Check the README.md and SETUP.md
2. Test locally with test_client.py
3. Check logs for errors
4. Review the evaluation requirements again

Good luck! 🚀
