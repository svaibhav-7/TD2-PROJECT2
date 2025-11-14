#!/bin/bash
# Quick start script for LLM Analysis Quiz

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║          LLM Analysis Quiz - Quick Start Setup                         ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "  Found: $python_version"
echo ""

# Create virtual environment
echo "✓ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Created: venv/"
else
    echo "  Already exists: venv/"
fi
echo ""

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate
echo "  Virtual environment activated"
echo ""

# Install dependencies
echo "✓ Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "  Installed all dependencies"
echo ""

# Install Playwright browsers
echo "✓ Installing Playwright browsers..."
python -m playwright install chromium > /dev/null 2>&1
echo "  Installed Chromium browser"
echo ""

# Create .env from template
if [ ! -f ".env" ]; then
    echo "✓ Creating .env file..."
    cp .env.example .env
    echo "  Created .env (configure with your values)"
else
    echo "✓ .env file exists"
fi
echo ""

# Show next steps
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                         Setup Complete! 🎉                            ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration:"
echo "   - EMAIL=your-email@example.com"
echo "   - SECRET_KEY=your-secret"
echo "   - OPENAI_API_KEY=sk-..."
echo ""
echo "2. Generate prompts for the form:"
echo "   python generate_prompts.py"
echo ""
echo "3. Test locally:"
echo "   python main.py"
echo ""
echo "4. In another terminal, run tests:"
echo "   python test_client.py"
echo ""
echo "5. Deploy to a public HTTPS endpoint"
echo ""
echo "6. Fill out the Google Form with your endpoint URL"
echo ""
echo "For detailed instructions, see SETUP.md"
echo ""
