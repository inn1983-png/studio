@echo off
chcp 65001 >nul 2>&1
cd /d "d:\ai-moive-studio\backend"
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
