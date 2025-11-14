@echo off
REM Quick start script for LLM Analysis Quiz (Windows)

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║          LLM Analysis Quiz - Quick Start Setup                         ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

REM Check Python version
echo ✓ Checking Python version...
python --version
echo.

REM Create virtual environment
echo ✓ Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo   Created: venv\
) else (
    echo   Already exists: venv\
)
echo.

REM Activate virtual environment
echo ✓ Activating virtual environment...
call venv\Scripts\activate.bat
echo   Virtual environment activated
echo.

REM Install dependencies
echo ✓ Installing dependencies...
pip install --upgrade pip > nul 2>&1
pip install -r requirements.txt > nul 2>&1
echo   Installed all dependencies
echo.

REM Install Playwright browsers
echo ✓ Installing Playwright browsers...
python -m playwright install chromium > nul 2>&1
echo   Installed Chromium browser
echo.

REM Create .env from template
if not exist ".env" (
    echo ✓ Creating .env file...
    copy .env.example .env > nul
    echo   Created .env (configure with your values)
) else (
    echo ✓ .env file exists
)
echo.

REM Show next steps
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                         Setup Complete! 🎉                            ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo Next steps:
echo 1. Edit .env with your configuration:
echo    - EMAIL=your-email@example.com
echo    - SECRET_KEY=your-secret
echo    - OPENAI_API_KEY=sk-...
echo.
echo 2. Generate prompts for the form:
echo    python generate_prompts.py
echo.
echo 3. Test locally:
echo    python main.py
echo.
echo 4. In another terminal, run tests:
echo    python test_client.py
echo.
echo 5. Deploy to a public HTTPS endpoint
echo.
echo 6. Fill out the Google Form with your endpoint URL
echo.
echo For detailed instructions, see SETUP.md
echo.
pause
