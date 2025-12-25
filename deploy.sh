#!/bin/bash
# QUICK DEPLOYMENT SCRIPT FOR PHASE 2

set -e  # Exit on error

echo "🚀 Starting Phase 2 Deployment..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Stopping containers...${NC}"
docker-compose down

echo ""
echo -e "${YELLOW}Step 2: Starting database...${NC}"
docker-compose up -d db
echo "Waiting 10 seconds for PostgreSQL to be ready..."
sleep 10

echo ""
echo -e "${YELLOW}Step 3: Running migrations...${NC}"
docker-compose run --rm backend python manage.py migrate

echo ""
echo -e "${YELLOW}Step 4: Checking if data exists...${NC}"
if docker-compose run --rm backend python check_data.py | grep -q "No products"; then
    echo -e "${YELLOW}No data found. Seeding demo data...${NC}"
    docker-compose run --rm backend python manage.py seed_demo_data
else
    echo -e "${GREEN}Data already exists. Skipping seed.${NC}"
fi

echo ""
echo -e "${YELLOW}Step 5: Starting all services...${NC}"
docker-compose up -d

echo ""
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 15

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🔍 Testing API endpoints..."
echo ""

# Test health
echo -n "Health check: "
if curl -s http://localhost:8001/api/health/ | grep -q "ok"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Test categories
echo -n "Categories API: "
CATEGORY_COUNT=$(curl -s http://localhost:8001/api/products/categories/ | grep -o '"count":[0-9]*' | grep -o '[0-9]*')
if [ "$CATEGORY_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ $CATEGORY_COUNT categories${NC}"
else
    echo -e "${RED}❌ No categories${NC}"
fi

# Test products
echo -n "Products API: "
PRODUCT_COUNT=$(curl -s http://localhost:8001/api/products/products/ | grep -o '"count":[0-9]*' | grep -o '[0-9]*')
if [ "$PRODUCT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ $PRODUCT_COUNT products${NC}"
else
    echo -e "${RED}❌ No products${NC}"
fi

echo ""
echo "🌐 Access URLs:"
echo "  - Kiosk Mode: http://localhost:5174/kiosk"
echo "  - Admin Panel: http://localhost:8001/admin (admin/admin123)"
echo "  - API Docs: http://localhost:8001/api/docs"
echo ""
echo "📝 View logs:"
echo "  - Backend: docker-compose logs -f backend"
echo "  - Frontend: docker-compose logs -f frontend"
echo ""
