#!/usr/bin/env python3
"""OPC Platform - 启动"""
import os, sys, uvicorn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
port = int(os.environ.get("PORT", 8000))
uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
