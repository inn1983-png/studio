@echo off
chcp 65001 >nul 2>&1
cd /d "C:\minio"
set MINIO_ROOT_USER=minioadmin
set MINIO_ROOT_PASSWORD=minioadmin123
minio.exe server C:\minio\data --console-address :9001
