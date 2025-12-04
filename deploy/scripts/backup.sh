#!/bin/bash
set -e

BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

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

mkdir -p "$BACKUP_DIR"

echo "📦 Backing up PostgreSQL..."
$COMPOSE_CMD -f docker-compose.prod.yml exec -T postgres pg_dump -U suna suna_ultra > "$BACKUP_DIR/db_$TIMESTAMP.sql"

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL backup complete: $BACKUP_DIR/db_$TIMESTAMP.sql"
else
    echo "❌ PostgreSQL backup failed"
    exit 1
fi

echo "📦 Backing up Redis..."
$COMPOSE_CMD -f docker-compose.prod.yml exec -T redis redis-cli BGSAVE

# Wait for BGSAVE to complete
sleep 3

REDIS_CONTAINER=$($COMPOSE_CMD -f docker-compose.prod.yml ps -q redis)
if [ -n "$REDIS_CONTAINER" ]; then
    docker cp $REDIS_CONTAINER:/data/dump.rdb "$BACKUP_DIR/redis_$TIMESTAMP.rdb"
    
    if [ $? -eq 0 ]; then
        echo "✅ Redis backup complete: $BACKUP_DIR/redis_$TIMESTAMP.rdb"
    else
        echo "⚠️  Redis backup failed"
    fi
else
    echo "⚠️  Redis container not found"
fi

echo ""
echo "✅ Backup complete: $BACKUP_DIR"
echo "   - db_$TIMESTAMP.sql"
echo "   - redis_$TIMESTAMP.rdb"
