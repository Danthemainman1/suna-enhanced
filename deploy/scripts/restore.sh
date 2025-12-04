#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file.sql>"
    echo ""
    echo "Example:"
    echo "  ./restore.sh ./backups/db_20240101_120000.sql"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

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

echo "⚠️  This will overwrite the current database!"
echo "Backup file: $BACKUP_FILE"
read -p "Continue? (y/N) " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

echo "📥 Restoring PostgreSQL from $BACKUP_FILE..."
$COMPOSE_CMD -f docker-compose.prod.yml exec -T postgres psql -U suna suna_ultra < "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Restore complete!"
else
    echo "❌ Restore failed"
    exit 1
fi
