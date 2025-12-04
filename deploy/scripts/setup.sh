#!/bin/bash
set -e

echo "🚀 Suna Ultra Setup"
echo "==================="

# Check dependencies
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }
if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose required"
    exit 1
fi

cd "$(dirname "$0")/../docker"

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    # Generate secrets
    SECRET_KEY=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -hex 16)
    
    # Use sed that works on both Linux and macOS
    if [ "$(uname)" = "Darwin" ]; then
        sed -i '' "s/generate-with-openssl-rand-hex-32/$SECRET_KEY/" .env
        sed -i '' "s/generate-secure-password/$DB_PASSWORD/" .env
    else
        sed -i "s/generate-with-openssl-rand-hex-32/$SECRET_KEY/" .env
        sed -i "s/generate-secure-password/$DB_PASSWORD/" .env
    fi
    
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your configuration:"
    echo "   - ANTHROPIC_API_KEY (required)"
    echo "   - SUPABASE_URL (required)"
    echo "   - SUPABASE_ANON_KEY (required)"
    echo "   - SUPABASE_SERVICE_ROLE_KEY (required)"
    echo "   - SUPABASE_JWT_SECRET (required)"
    echo ""
    echo "   Then run: ./setup.sh again"
    echo ""
    exit 0
fi

# Check API key
if grep -q "your-api-key-here" .env; then
    echo "❌ Please set ANTHROPIC_API_KEY in .env"
    exit 1
fi

# Check Supabase configuration
if grep -q "your-supabase-url" .env; then
    echo "❌ Please set Supabase configuration in .env"
    exit 1
fi

echo "📦 Pulling images..."
$COMPOSE_CMD -f docker-compose.prod.yml pull

echo "🏗️  Building images..."
$COMPOSE_CMD -f docker-compose.prod.yml build

echo "🚀 Starting services..."
$COMPOSE_CMD -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services..."
sleep 20

# Health check
echo "🏥 Checking health..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost/health > /dev/null 2>&1; then
        echo ""
        echo "✅ Suna Ultra is running!"
        echo ""
        echo "   API:  http://localhost/api"
        echo "   Docs: http://localhost/docs"
        echo ""
        echo "📊 View logs:"
        echo "   $COMPOSE_CMD -f docker-compose.prod.yml logs -f"
        echo ""
        exit 0
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting for services... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 5
done

echo "❌ Health check failed. Check logs with:"
echo "   $COMPOSE_CMD -f docker-compose.prod.yml logs"
exit 1
