#!/usr/bin/env python3
"""OPC Platform - 启动"""
import os, sys

# 确保项目根目录在 path
root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root)
os.chdir(root)

import uvicorn
port = int(os.environ.get("PORT", 10000))
print(f"🚀 Starting OPC Platform on port {port}")
print(f"📁 Root: {root}")
print(f"📁 CWD: {os.getcwd()}")
uvicorn.run("app.main:app", host="0.0.0.0", port=port)
