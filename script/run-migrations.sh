#!/bin/bash
# Wait for database to be ready
echo "Waiting for database..."
sleep 5

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Check if superuser exists, if not create one
echo "Checking for superuser..."
python manage.py shell << PYTHON
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
PYTHON

echo "Migrations complete!"
