#!/bin/bash

cd "$(dirname "$0")/../docker"

# Detect docker compose command
if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose not found"
    exit 1
fi

check_service() {
    if curl -sf "$1" > /dev/null 2>&1; then
        echo "✅ $2"
        return 0
    else
        echo "❌ $2"
        return 1
    fi
}

echo "🏥 Health Check"
echo "==============="
echo ""

FAILED=0

check_service "http://localhost/health" "Backend API" || FAILED=$((FAILED + 1))
check_service "http://localhost/docs" "API Docs" || FAILED=$((FAILED + 1))

echo ""
echo "📊 Container Status:"
echo ""
$COMPOSE_CMD -f docker-compose.prod.yml ps

echo ""
if [ $FAILED -eq 0 ]; then
    echo "✅ All services healthy"
    exit 0
else
    echo "⚠️  $FAILED service(s) unhealthy"
    exit 1
fi
