#!/bin/bash

# 🧪 Quick Deployment Test Script
# This script verifies all Docker services are running correctly

set -e

echo "🚀 Starting F&B POS System Deployment Test..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Docker is running
echo "📦 Step 1: Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Step 2: Pull latest code
echo "📥 Step 2: Pulling latest code from GitHub..."
git pull origin main
echo -e "${GREEN}✅ Code updated${NC}"
echo ""

# Step 3: Stop existing containers
echo "🛑 Step 3: Stopping existing containers..."
docker-compose down
echo -e "${GREEN}✅ Containers stopped${NC}"
echo ""

# Step 4: Build containers
echo "🔨 Step 4: Building containers (this may take a few minutes)..."
docker-compose build --no-cache
echo -e "${GREEN}✅ Containers built${NC}"
echo ""

# Step 5: Start services
echo "▶️  Step 5: Starting services..."
docker-compose up -d
echo -e "${GREEN}✅ Services started${NC}"
echo ""

# Step 6: Wait for services to be ready
echo "⏳ Step 6: Waiting for services to be ready..."
sleep 10

# Check if all containers are running
echo ""
echo "📊 Container Status:"
docker-compose ps
echo ""

# Step 7: Check service health
echo "🏥 Step 7: Checking service health..."

# Check PostgreSQL
if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not ready${NC}"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is ready${NC}"
else
    echo -e "${RED}❌ Redis is not ready${NC}"
fi

# Check Backend API
if curl -f http://localhost:8001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API is responding${NC}"
else
    echo -e "${YELLOW}⚠️  Backend API not responding yet (may need migration)${NC}"
fi

# Check Frontend
if curl -f http://localhost:5174 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is responding${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend not responding yet${NC}"
fi

echo ""

# Step 8: Run migrations
echo "🗃️  Step 8: Running database migrations..."
if docker-compose exec -T backend python manage.py migrate; then
    echo -e "${GREEN}✅ Migrations completed${NC}"
else
    echo -e "${RED}❌ Migration failed${NC}"
    exit 1
fi
echo ""

# Step 9: Seed dummy data
echo "🌱 Step 9: Seeding dummy data..."
if docker-compose exec -T backend python manage.py seed_demo_data; then
    echo -e "${GREEN}✅ Dummy data seeded${NC}"
else
    echo -e "${YELLOW}⚠️  Seed data may already exist (skipping)${NC}"
fi
echo ""

# Final status
echo "🎉 Deployment Complete!"
echo ""
echo "📍 Access Points:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🖥️  Kiosk Mode:${NC}     http://localhost:5174/kiosk"
echo -e "${GREEN}👤 Admin Panel:${NC}    http://localhost:8001/admin"
echo -e "                     ${YELLOW}Username: admin${NC}"
echo -e "                     ${YELLOW}Password: admin123${NC}"
echo -e "${GREEN}📖 API Docs:${NC}       http://localhost:8001/api/docs"
echo -e "${GREEN}🔌 Backend API:${NC}    http://localhost:8001/api"
echo -e "${GREEN}🌐 Nginx Proxy:${NC}   http://localhost:8082"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 View logs:"
echo "  docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "  docker-compose down"
echo ""
echo "✨ Happy testing! ✨"
