#!/bin/bash
# Multi-Outlet Test Data Setup Script for Docker
# Run this script to setup test data with outlets inside Docker container

echo "🚀 Starting Multi-Outlet Test Data Setup via Docker..."
echo ""

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Check if containers are running
if ! docker-compose ps | grep -q "backend"; then
    echo "⚠️  Backend container not running. Starting containers..."
    docker-compose up -d
    echo "⏳ Waiting for services to be ready..."
    sleep 5
fi

echo "📦 Executing multi-outlet setup script in backend container..."
echo ""

# Execute the Python script inside container
docker-compose exec backend python setup_multi_outlet_test_data.py

echo ""
echo "✅ Multi-outlet setup complete!"
echo "📊 Created: 3 tenants, 6 outlets, 20 users, 12 products"
echo "🔗 Access admin panel at: http://localhost:5175/"
