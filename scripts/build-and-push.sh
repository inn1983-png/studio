#!/bin/bash
# Docker 镜像构建和推送脚本
# 用法: ./build-and-push.sh [version]

set -e

VERSION=${1:-latest}
REGISTRY="docker.io"
USERNAME="txtovideo"

echo "🚀 开始构建和推送 Docker 镜像..."
echo "📦 版本: $VERSION"
echo "🏷️  仓库: $REGISTRY/$USERNAME"
echo ""

# 检查是否已登录
if ! docker info | grep -q "Username"; then
    echo "⚠️  请先登录 Docker Hub:"
    echo "   docker login"
    exit 1
fi

# 构建后端镜像
echo "🔨 构建后端镜像..."
docker build -t $REGISTRY/$USERNAME/txtovideo-backend:$VERSION ./backend
docker tag $REGISTRY/$USERNAME/txtovideo-backend:$VERSION $REGISTRY/$USERNAME/txtovideo-backend:latest

# 构建前端镜像
echo "🔨 构建前端镜像..."
docker build -t $REGISTRY/$USERNAME/txtovideo-frontend:$VERSION ./frontend
docker tag $REGISTRY/$USERNAME/txtovideo-frontend:$VERSION $REGISTRY/$USERNAME/txtovideo-frontend:latest

# 推送镜像
echo "📤 推送后端镜像..."
docker push $REGISTRY/$USERNAME/txtovideo-backend:$VERSION
docker push $REGISTRY/$USERNAME/txtovideo-backend:latest

echo "📤 推送前端镜像..."
docker push $REGISTRY/$USERNAME/txtovideo-frontend:$VERSION
docker push $REGISTRY/$USERNAME/txtovideo-frontend:latest

echo ""
echo "✅ 所有镜像已成功推送!"
echo ""
echo "📋 已推送的镜像:"
echo "   - $REGISTRY/$USERNAME/txtovideo-backend:$VERSION"
echo "   - $REGISTRY/$USERNAME/txtovideo-backend:latest"
echo "   - $REGISTRY/$USERNAME/txtovideo-frontend:$VERSION"
echo "   - $REGISTRY/$USERNAME/txtovideo-frontend:latest"
