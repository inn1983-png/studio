@echo off
chcp 65001 >nul 2>&1
title Txtovideo Studio - 停止服务

echo.
echo  正在停止 Txtovideo Studio 服务...
echo.

taskkill /fi "WINDOWTITLE eq Txtovideo Studio - MinIO*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq Txtovideo Studio - Backend*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq Txtovideo Studio - Frontend*" /f >nul 2>&1

echo  所有服务已停止。
echo.
pause
