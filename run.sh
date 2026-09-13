#!/usr/bin/env bash

set -e

echo "🚀 Launching Marketing Data Hub..."

# 1. Setup Python Virtual Environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Virtual Environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "📥 Installing Python dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install fastapi uvicorn sqlalchemy pydantic
fi

# 2. Setup Node dependencies
if [ -d "frontend" ]; then
    echo "📦 Installing Node dependencies..."
    (cd frontend && npm install)
fi

# 3. Clean up legacy artifacts (.DS_Store)
echo "🧹 Cleaning up system artifacts..."
find . -name ".DS_Store" -depth -exec rm {} \; 2>/dev/null || true

# 4. Optional Database Reset Prompt
if [ "$1" == "--reset-db" ]; then
    echo "🗑️  Resetting SQLite Database..."
    rm -f marketing_data.db
fi

# 5. Trap process termination signals to clean up background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill 0
    exit 0
}
trap cleanup SIGINT SIGTERM

# 6. Start FastAPI Backend (Port 8000)
echo "⚡ Starting FastAPI Backend on http://localhost:8000..."
uvicorn src.api.main:app --reload --port 8000 &

# 7. Start React Frontend (Vite)
if [ -d "frontend" ]; then
    echo "🌐 Starting React Vite Frontend..."
    (cd frontend && npm run dev) &
fi

# Wait for background jobs
wait
