cd kiosk-svelte
docker-compose down

git pull origin main

# Atau jika ada perubahan lokal
git fetch origin main
git merge origin/main

docker-compose up --build -d
docker-compose exec backend python manage.py makemigrations
docker-compose run --rm backend python manage.py migrate
docker-compose exec backend python manage.py seed_demo_data
docker-compose exec backend python manage.py seed_foodcourt
docker-compose exec backend python manage.py seed_promotion
docker-compose exec backend python manage.py seed_customer

docker-compose logs frontend --tail=50
docker-compose restart frontend
docker-compose restart admin

docker-compose down frontend; docker-compose up -d frontend
docker-compose build frontend; docker-compose up -d frontend

Untuk ke depannya, jika ada masalah dependency:
docker-compose build frontend
docker-compose up -d frontend

Start-Sleep -Seconds 15; docker-compose logs frontend --tail=20
Start-Sleep -Seconds 10; docker-compose logs frontend --tail=15 | Select-String "error|ready" | Select-Object -Last 5
docker-compose logs frontend 2>&1 | Select-String "ready in|error" | Select-Object -Last 3

URLs PENTING
Kiosk: http://localhost:5174/kiosk
Kitchen: http://localhost:5174/kitchen
API Docs: http://localhost:8001/api/docs/
Django Admin: http://localhost:8001/admin/
GitHub: https://github.com/dadinjaenudin/kiosk-svelte
