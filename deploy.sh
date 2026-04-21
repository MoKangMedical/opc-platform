#!/bin/bash
PORT=${1:-8090}
echo "🚀 opc-platform 部署中..."
cd "$(dirname "$0")"
python3 -c "import fastapi" 2>/dev/null || pip3 install fastapi uvicorn
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT &
sleep 2
echo "✅ opc-platform 已启动: http://localhost:$PORT"
