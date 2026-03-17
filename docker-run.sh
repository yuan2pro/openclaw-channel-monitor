#!/bin/bash
# Build and run OpenClaw Monitor in Docker

set -e

IMAGE_NAME="openclaw-monitor"
CONTAINER_NAME="openclaw-monitor"

echo "🐳 Building Docker image..."
docker build -t $IMAGE_NAME .

echo "🛑 Stopping existing container if running..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

echo "🚀 Starting container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p 5050:5050 \
    -v /home/n100/.openclaw:/root/.openclaw:ro \
    -e TZ=Asia/Shanghai \
    --restart unless-stopped \
    $IMAGE_NAME

echo "✅ Container started!"
echo "📍 Dashboard: http://localhost:5050"
echo ""
echo "📋 Commands:"
echo "  docker logs -f $CONTAINER_NAME   # View logs"
echo "  docker stop $CONTAINER_NAME      # Stop container"
echo "  docker restart $CONTAINER_NAME   # Restart container"