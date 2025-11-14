# Project Completion Checklist

Use this checklist to track your progress through the LLM Analysis Quiz project.

## Phase 1: Local Setup ✓

- [ ] Clone or initialize Git repository
- [ ] Run setup script (`setup.sh` on Linux/Mac or `setup.bat` on Windows)
- [ ] OR manually create virtual environment and install requirements
- [ ] Verify Python dependencies installed: `pip list | grep -E "flask|openai|playwright"`
- [ ] Copy `.env.example` to `.env`
- [ ] Edit `.env` with your values:
  - [ ] EMAIL (your email address)
  - [ ] SECRET_KEY (your secret string, min 10 chars)
  - [ ] OPENAI_API_KEY (from platform.openai.com/api-keys)
- [ ] Verify environment loads: `python config.py`

## Phase 2: Prompt Engineering ✓

- [ ] Read `PROMPT_GUIDE.md` to understand strategies
- [ ] Run `python generate_prompts.py` to see recommendations
- [ ] Understand 5 system prompt strategies (defense)
- [ ] Understand 5 user prompt strategies (attack)
- [ ] Choose or generate your system prompt (max 100 chars)
- [ ] Choose or generate your user prompt (max 100 chars)
- [ ] Test prompts locally (if OpenAI key configured)
- [ ] Document why you chose each strategy

## Phase 3: Local Testing ✓

- [ ] Start server: `python main.py`
- [ ] In another terminal, run: `python test_client.py`
- [ ] Verify all 5 tests pass:
  - [ ] Health Check: ✓ PASSED
  - [ ] Invalid JSON: ✓ PASSED (returns 400)
  - [ ] Missing Fields: ✓ PASSED (returns 400)
  - [ ] Invalid Secret: ✓ PASSED (returns 403)
  - [ ] Valid Request: ✓ PASSED (returns 200)
- [ ] Check logs for errors: `tail -f quiz_solver.log`

## Phase 4: Code Review ✓

- [ ] Review `app.py` - Flask endpoints are correct
- [ ] Review `quiz_solver.py` - Headless browser logic is sound
- [ ] Review `data_processor.py` - Data processing utilities are complete
- [ ] Review `prompt_utils.py` - Prompt strategies are well-documented
- [ ] Ensure no hardcoded API keys or secrets in code
- [ ] Add comments explaining complex logic
- [ ] Verify error handling in all functions

## Phase 5: Documentation ✓

- [ ] README.md - Project overview and quick start
- [ ] SETUP.md - Comprehensive deployment guide
- [ ] PROMPT_GUIDE.md - Prompt engineering explanation
- [ ] PROJECT_OVERVIEW.md - File structure overview
- [ ] Add docstrings to all functions and classes
- [ ] Add comments explaining key algorithms
- [ ] Create DEPLOYMENT.md (if deployment method is complex)

## Phase 6: Git Repository ✓

- [ ] Initialize Git: `git init`
- [ ] Create `.gitignore` (already created)
- [ ] Add all files: `git add .`
- [ ] Initial commit: `git commit -m "Initial commit"`
- [ ] Create GitHub repository (make it PUBLIC later after evaluation request)
- [ ] Add remote: `git remote add origin https://github.com/YOUR_USERNAME/your-repo.git`
- [ ] Push to GitHub: `git push -u origin main`
- [ ] Verify `.env` is NOT in repository (should be in .gitignore)
- [ ] Verify `LICENSE` file is present and visible

## Phase 7: Deployment ✓

- [ ] Choose deployment platform:
  - [ ] Heroku
  - [ ] Azure
  - [ ] AWS
  - [ ] DigitalOcean/Linode
  - [ ] Other: _______
- [ ] Follow deployment steps for chosen platform
- [ ] Verify endpoint is accessible: `curl https://your-endpoint/health`
- [ ] Set environment variables on production:
  - [ ] EMAIL
  - [ ] SECRET_KEY
  - [ ] OPENAI_API_KEY
- [ ] Test production endpoint with demo:
  ```bash
  curl -X POST https://your-endpoint/quiz \
    -H "Content-Type: application/json" \
    -d '{"email":"your@email.com","secret":"your-secret","url":"https://tds-llm-analysis.s-anand.net/demo"}'
  ```
- [ ] Verify response is HTTP 200 with valid JSON

## Phase 8: Google Form Submission ✓

- [ ] Go to the Google Form (link provided)
- [ ] Fill in your email address
- [ ] Fill in your SECRET_KEY (must match your .env)
- [ ] Fill in system prompt (max 100 chars) from Phase 2
- [ ] Fill in user prompt (max 100 chars) from Phase 2
- [ ] Fill in API endpoint URL (https://..., NOT http://)
- [ ] Fill in GitHub repository URL (make sure it's public or will be made public)
- [ ] Verify all fields are correct
- [ ] Submit form
- [ ] Receive confirmation

## Phase 9: Pre-Evaluation Checks ✓

- [ ] Verify GitHub repo is PUBLIC
- [ ] Verify MIT LICENSE is present in repo
- [ ] Verify `README.md` is in root directory
- [ ] Verify `SETUP.md` has clear instructions
- [ ] Verify all documentation is clear and complete
- [ ] Test endpoint one more time from different network (if possible)
- [ ] Check logs for any errors from previous submissions
- [ ] Verify SECRET_KEY is secure (not easily guessable)
- [ ] Verify OPENAI_API_KEY is set correctly on production
- [ ] Monitor application logs during evaluation window

## Phase 10: Evaluation (Nov 29, 3-4 PM IST)

- [ ] Ensure server is running and healthy
- [ ] Monitor logs in real-time
- [ ] Keep application resources available (don't restart)
- [ ] Have OpenAI API quota available
- [ ] Keep internet connection stable
- [ ] Be ready to debug if issues arise

## Phase 11: Viva Preparation

- [ ] Prepare explanation of your system prompt choice:
  - [ ] Why did you choose this strategy?
  - [ ] How does it prevent code word extraction?
  - [ ] What are its strengths and weaknesses?
- [ ] Prepare explanation of your user prompt choice:
  - [ ] Why did you choose this strategy?
  - [ ] How does it extract the code word?
  - [ ] What are its strengths and weaknesses?
- [ ] Prepare explanation of API design:
  - [ ] How does secret verification work?
  - [ ] How do you handle the 3-minute timeout?
  - [ ] How do you handle retries?
- [ ] Prepare explanation of data processing:
  - [ ] What types of data can you process? (CSV, PDF, JSON, web scraping)
  - [ ] How do you use LLM for complex questions?
  - [ ] How do you generate answers?
- [ ] Test your audio/video setup for viva
- [ ] Have GitHub repository open and ready to discuss

## Phase 12: After Evaluation

- [ ] Receive results and feedback
- [ ] Document lessons learned
- [ ] Consider improvements for future projects
- [ ] Share your approach with peers (if appropriate)

---

## Submission Summary Template

Print this and fill it in:

```
PROJECT SUBMISSION CHECKLIST
=============================

Email: ___________________________________
Secret Key: ______________________________ (keep private!)
System Prompt (max 100 chars): ___________
  Length: ___ / 100 chars ✓

User Prompt (max 100 chars): _____________
  Length: ___ / 100 chars ✓

API Endpoint: ____________________________
  Scheme: https:// (not http://) ✓
  Publicly accessible: Yes ✓
  Response to /health: HTTP 200 ✓

GitHub Repository: _______________________
  Is public: Yes ✓
  Contains LICENSE: Yes ✓
  Contains README.md: Yes ✓
  Contains SETUP.md: Yes ✓

Evaluation Window: November 29, 2025, 3-4 PM IST
Viva: TBD (check email for date/time)
```

---

## Important Reminders

⚠️ **Before Evaluation (Nov 29)**:
1. Your endpoint must be **HTTPS** (not HTTP)
2. Your endpoint must be **publicly accessible**
3. You must return **HTTP 200 with valid JSON** for valid requests
4. You must return **HTTP 403** for invalid secrets
5. You must return **HTTP 400** for invalid JSON
6. You must solve quizzes **within 3 minutes**
7. Your **GitHub repo must be public** with MIT LICENSE

⚠️ **During Evaluation**:
1. Monitor your application logs
2. Keep your server running
3. Be ready to debug issues
4. Have sufficient API quota available
5. Don't restart the server

⚠️ **Before Viva**:
1. Be ready to explain your prompt choices
2. Have your repository open for discussion
3. Test your audio/video setup
4. Have internet backup plan
5. Be prepared to defend your design decisions

---

## Help & Support

If you get stuck:

1. Check `SETUP.md` for setup issues
2. Check `PROMPT_GUIDE.md` for prompt strategy questions
3. Check `README.md` for quick overview
4. Run `python test_client.py` to debug API issues
5. Check logs: `tail -f quiz_solver.log`
6. Review error messages carefully

---

**Checklist Version**: 1.0
**Last Updated**: November 14, 2025
**Status**: Ready for completion! ✓

Good luck! 🚀
