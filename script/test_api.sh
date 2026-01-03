#!/bin/bash
# Quick API test script

echo "🔍 Testing Product API endpoints..."
echo ""

echo "1. Health Check:"
curl -s http://localhost:8001/api/health/ | python3 -m json.tool || echo "Failed"
echo ""

echo "2. Categories API:"
curl -s http://localhost:8001/api/products/categories/ | python3 -m json.tool | head -30 || echo "Failed"
echo ""

echo "3. Products API:"
curl -s http://localhost:8001/api/products/products/ | python3 -m json.tool | head -30 || echo "Failed"
echo ""

echo "✅ API Test Complete"
