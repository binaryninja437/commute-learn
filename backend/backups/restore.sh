#!/bin/bash
# SaarLM Emergency Restore Script
# Run this if the app breaks: bash backend/backups/restore.sh

echo "🔧 Restoring SaarLM to last working version..."
echo ""

# Navigate to project root if not there
if [ ! -d "backend" ]; then
    cd ../..
fi

# Backup current broken files first
echo "📦 Creating backup of current (possibly broken) files..."
mkdir -p backend/backups/broken_backup_$(date +%Y%m%d_%H%M%S)
BROKEN_DIR="backend/backups/broken_backup_$(date +%Y%m%d_%H%M%S)"

cp backend/main.py "$BROKEN_DIR/main.py" 2>/dev/null
cp backend/services/ocr_service.py "$BROKEN_DIR/ocr_service.py" 2>/dev/null
cp backend/services/script_generator.py "$BROKEN_DIR/script_generator.py" 2>/dev/null
cp backend/services/tts_service.py "$BROKEN_DIR/tts_service.py" 2>/dev/null
cp frontend/src/App.jsx "$BROKEN_DIR/App.jsx" 2>/dev/null

echo "✅ Broken files backed up to: $BROKEN_DIR"
echo ""

# Restore working files
echo "🔄 Restoring working files..."
cp backend/backups/main_working_v1.py backend/main.py
cp backend/backups/ocr_service_working_v1.py backend/services/ocr_service.py
cp backend/backups/script_generator_working_v1.py backend/services/script_generator.py
cp backend/backups/tts_service_working_v1.py backend/services/tts_service.py
cp backend/backups/App_working_v1.jsx frontend/src/App.jsx
cp backend/backups/.env.backup backend/.env 2>/dev/null

echo "✅ Restore complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Stop any running backend servers (Ctrl+C)"
echo "  2. Start backend with:"
echo "     cd backend"
echo "     set PYTHONIOENCODING=utf-8 && venv311/Scripts/python.exe -m uvicorn main:app --reload --port 8001"
echo ""
echo "  3. Frontend should auto-reload (http://localhost:3002)"
echo ""
echo "✅ All systems ready!"
