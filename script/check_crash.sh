#!/bin/bash

echo "🚨 BACKEND CRASH DETECTOR"
echo "=========================="
echo ""

echo "1. Check if backend is running:"
echo "------------------------------"
docker-compose ps backend

echo ""
echo "2. Backend logs (last 100 lines):"
echo "--------------------------------"
docker-compose logs backend --tail 100

echo ""
echo "3. Try to restart backend:"
echo "------------------------"
docker-compose restart backend

echo ""
echo "Waiting 10 seconds..."
sleep 10

echo ""
echo "4. Check if backend is up:"
echo "------------------------"
docker-compose ps backend

echo ""
echo "5. Test health endpoint:"
echo "----------------------"
curl http://localhost:8001/api/health/ 2>&1 || echo "FAILED"

echo ""
echo "6. New backend logs:"
echo "------------------"
docker-compose logs backend --tail 50

echo ""
echo "================================"
echo "If backend keeps crashing, there's a code error."
echo "Check the logs above for Python tracebacks."
echo ""
