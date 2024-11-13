#!/bin/bash
cd backend
export PORT="${PORT:-8000}"
python main.py
