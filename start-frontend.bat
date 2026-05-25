@echo off
chcp 65001 >nul 2>&1
cd /d "d:\ai-moive-studio\frontend"
npx vite --port 5173 --strictPort
