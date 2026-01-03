#!/bin/bash

# 🚀 Quick Setup Script for F&B POS System
# This script will setup and start all services

set -e

echo "🚀 Starting F&B POS System Setup..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Pull latest changes
echo -e "${YELLOW}📥 Step 1: Pulling latest code...${NC}"
git pull origin main
echo -e "${GREEN}✅ Code updated${NC}"
echo ""

# Step 2: Setup environment files
echo -e "${YELLOW}📝 Step 2: Setting up environment files...${NC}"
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✅ Created backend/.env${NC}"
else
    echo "ℹ️  backend/.env already exists"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo -e "${GREEN}✅ Created frontend/.env${NC}"
else
    echo "ℹ️  frontend/.env already exists"
fi
echo ""

# Step 3: Stop old containers
echo -e "${YELLOW}🛑 Step 3: Stopping old containers...${NC}"
docker-compose down -v
echo -e "${GREEN}✅ Old containers stopped${NC}"
echo ""

# Step 4: Build containers
echo -e "${YELLOW}🔨 Step 4: Building containers (this may take 3-5 minutes)...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✅ Containers built${NC}"
echo ""

# Step 5: Start services
echo -e "${YELLOW}▶️  Step 5: Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ Services started${NC}"
echo ""

# Step 6: Wait for backend to be ready
echo -e "${YELLOW}⏳ Step 6: Waiting for backend to be ready...${NC}"
echo "This includes running database migrations..."
sleep 20

# Check if backend is healthy
for i in {1..30}; do
    if curl -f http://localhost:8001/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    echo "Waiting for backend... ($i/30)"
    sleep 2
done
echo ""

# Step 7: Seed demo data
echo -e "${YELLOW}🌱 Step 7: Seeding demo data...${NC}"
docker-compose exec -T backend python manage.py seed_demo_data || echo "⚠️  Demo data may already exist"
echo -e "${GREEN}✅ Demo data seeded${NC}"
echo ""

# Step 8: Show container status
echo -e "${YELLOW}📊 Step 8: Checking container status...${NC}"
docker-compose ps
echo ""

# Final message
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Access Points:"
echo "  🖥️  Kiosk Mode:    http://localhost:5174/kiosk"
echo "  👤 Admin Panel:   http://localhost:8001/admin"
echo "                    Username: admin"
echo "                    Password: admin123"
echo "  📖 API Docs:      http://localhost:8001/api/docs"
echo "  🌐 Nginx:         http://localhost:8082"
echo ""
echo "📦 Demo Data:"
echo "  • 20 Products (Nasi Goreng, Mie Goreng, Es Teh, etc.)"
echo "  • 5 Categories"
echo "  • 2 Users (admin, cashier)"
echo "  • 2 Outlets"
echo ""
echo "📊 Useful Commands:"
echo "  • View logs:       docker-compose logs -f"
echo "  • Stop services:   docker-compose down"
echo "  • Restart:         docker-compose restart"
echo ""
echo "✨ Happy Testing! ✨"
