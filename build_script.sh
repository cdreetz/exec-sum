#!/bin/bash

# Frontend setup first
echo "Setting up frontend..."
cd frontend

# Install dependencies if node_modules doesn't exist or package.json was modified
if [ ! -d "node_modules" ] || [ package.json -nt node_modules ]; then
    echo "Installing npm dependencies..."
    npm install
else
    echo "Node modules are up to date"
fi

echo "Building frontend..."
npm run build


# Backend setup
echo "Setting up backend..."
cd ../backend

# Wait for frontend build to complete and verify directories exist
if [ ! -d "../frontend/build" ] || [ ! -d "../frontend/build/static" ]; then
    echo "Error: Frontend build directories not found. Please ensure frontend build completed successfully."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "env" ]; then
    echo "Creating new virtual environment..."
    python3 -m venv env
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
source env/bin/activate

# Install/update requirements
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Add trap to handle cleanup when script is interrupted
cleanup() {
    echo "Cleaning up..."
    pkill -f "python main.py"
    deactivate
    exit 0
}

# Set up trap for SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Check if FastAPI is already running
if ! pgrep -f "python main.py" > /dev/null; then
    echo "Starting FastAPI server..."
    python main.py
else
    echo "FastAPI server is already running"
fi

# Keep script running to handle Ctrl+C properly
wait