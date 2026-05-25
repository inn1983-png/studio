@echo off
chcp 65001 >nul 2>&1
title Txtovideo Studio - 一键启动

echo.
echo  ========================================
echo    Txtovideo Studio - 一键启动
echo  ========================================
echo.

set "PROJECT_DIR=%~dp0"

echo [1/3] 启动 MinIO 文件存储...
start "Txtovideo Studio - MinIO" "%PROJECT_DIR%start-minio.bat"
echo [OK] MinIO 启动中 (API: http://localhost:9000, 控制台: http://localhost:9001)

echo.
echo [2/3] 启动后端服务...
if not exist "%PROJECT_DIR%.env" (
    if exist "%PROJECT_DIR%.env.example" (
        echo [提示] 未找到 .env 文件，从 .env.example 复制...
        copy "%PROJECT_DIR%.env.example" "%PROJECT_DIR%.env" >nul
    )
)

start "Txtovideo Studio - Backend" "%PROJECT_DIR%start-backend.bat"
echo [OK] 后端服务启动中 (http://localhost:8000)

echo.
echo [3/3] 启动前端服务...
if not exist "%PROJECT_DIR%frontend\node_modules" (
    echo [提示] 首次运行，安装前端依赖...
    cd /d "%PROJECT_DIR%frontend"
    call npm install
    if %errorlevel% neq 0 (
        echo [错误] 前端依赖安装失败
        pause
        exit /b 1
    )
)

start "Txtovideo Studio - Frontend" "%PROJECT_DIR%start-frontend.bat"
echo [OK] 前端服务启动中 (http://localhost:5173)

echo.
timeout /t 5 /nobreak >nul

echo.
echo  ========================================
echo    启动完成！
echo    前端:    http://localhost:5173
echo    后端:    http://localhost:8000
echo    API文档: http://localhost:8000/docs
echo    MinIO:   http://localhost:9001
echo      用户名: minioadmin
echo      密码:   minioadmin123
echo  ========================================
echo.
echo  按任意键打开浏览器...
pause >nul

start http://localhost:5173
