#!/bin/bash

# Commute & Learn - Startup Script
# Run this to start both backend and frontend

echo "🎧 Commute & Learn - Starting up..."
echo "=================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for required tools
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js required but not installed."; exit 1; }
command -v ffmpeg >/dev/null 2>&1 || { echo "⚠️  ffmpeg not found. Audio generation may fail."; }

# Start Backend
echo -e "${BLUE}📦 Starting Backend...${NC}"
cd backend

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install dependencies
pip install -q -r requirements.txt

# Start backend in background
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend running on http://localhost:8000${NC}"

# Start Frontend
echo -e "${BLUE}🎨 Starting Frontend...${NC}"
cd ../frontend

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend running on http://localhost:3000${NC}"

echo ""
echo "=================================="
echo -e "${GREEN}🎉 Commute & Learn is ready!${NC}"
echo ""
echo "📱 Open: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=================================="

# Wait for Ctrl+C
trap "echo ''; echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
