#!/bin/bash
set -e

echo "🚀 Deploying Suna Ultra..."

cd "$(dirname "$0")/../docker"

# Detect docker compose command
if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose required"
    exit 1
fi

# Pull latest images
echo "📦 Pulling latest images..."
$COMPOSE_CMD -f docker-compose.prod.yml pull

# Rebuild images
echo "🏗️  Building images..."
$COMPOSE_CMD -f docker-compose.prod.yml build

# Restart with zero downtime
echo "🔄 Restarting services..."
$COMPOSE_CMD -f docker-compose.prod.yml up -d --no-deps --build backend worker

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Health check
if curl -sf http://localhost/health > /dev/null 2>&1; then
    echo "✅ Deployed successfully!"
else
    echo "⚠️  Services restarted but health check failed. Check logs:"
    echo "   $COMPOSE_CMD -f docker-compose.prod.yml logs"
fi
