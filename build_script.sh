#!/bin/bash

# Exit on any error
set -e

echo "Starting build process..."

# Frontend setup
echo "=== Setting up frontend ==="
cd frontend
echo "Installing npm dependencies..."
npm install
echo "Building frontend..."
npm run build

# Verify frontend build
if [ ! -d "build" ] || [ ! -d "build/static" ]; then
  echo "Error: Frontend build directories not found. Build failed."
  exit 1
fi

# Backend setup
echo "=== Setting up backend ==="
cd ../backend
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "=== Build completed successfully ==="
