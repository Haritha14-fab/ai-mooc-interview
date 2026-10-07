#!/bin/bash
# AI MOOC Interview & Assessment System - Setup Script

echo ""
echo "===================================="
echo "AI MOOC Setup Script"
echo "===================================="
echo ""

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null
then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "Python: $(python3 --version)"
echo "Node.js: $(node --version)"
echo ""

# Setup Backend
echo "===================================="
echo "Setting up Backend..."
echo "===================================="
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update backend/.env with your API keys"
fi

echo "Backend setup complete!"
echo ""
cd ..

# Setup Frontend
echo "===================================="
echo "Setting up Frontend..."
echo "===================================="
cd frontend

echo "Installing Node dependencies..."
npm install

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo "Frontend setup complete!"
echo ""
cd ..

echo ""
echo "===================================="
echo "Setup Complete!"
echo "===================================="
echo ""
echo "To run the application:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python -m uvicorn app.main:app --reload"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:3000"
echo ""
echo "Demo Credentials:"
echo "  Email: demo@example.com"
echo "  Password: demo1234"
echo ""
