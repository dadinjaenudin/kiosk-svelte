#!/bin/bash
# Reset and regenerate migrations for products app

echo "🔧 Fixing Products Migrations..."
echo ""

# Show current state
echo "Current migrations in products app:"
ls -la backend/apps/products/migrations/

echo ""
echo "⚠️  This script will:"
echo "1. Keep existing migration files (backup approach)"
echo "2. Run makemigrations to create missing migrations"
echo "3. Show what needs to be migrated"
echo ""

# Check if inside Docker or local
if [ -f /.dockerenv ]; then
    echo "Running inside Docker container"
    python manage.py makemigrations products
    echo ""
    echo "Migration files created. Run 'python manage.py migrate' to apply."
else
    echo "Running from host - using docker-compose"
    docker-compose exec backend python manage.py makemigrations products
    echo ""
    echo "Migration files created. Run 'docker-compose exec backend python manage.py migrate' to apply."
fi

echo ""
echo "✅ Done! Check the migrations created."
