#!/bin/bash

echo "🧪 PHASE 2 BACKEND VERIFICATION"
echo "==============================="
echo ""

echo "📦 1. Check Core App Files"
echo "----------------------------"
echo "✓ Core Models:"
ls -lah backend/apps/core/models.py 2>/dev/null && echo "  ✅ models.py exists" || echo "  ❌ models.py missing"

echo "✓ Core Permissions:"
ls -lah backend/apps/core/permissions.py 2>/dev/null && echo "  ✅ permissions.py exists" || echo "  ❌ permissions.py missing"

echo "✓ Core Middleware:"
ls -lah backend/apps/tenants/middleware.py 2>/dev/null && echo "  ✅ middleware.py exists" || echo "  ❌ middleware.py missing"

echo ""
echo "📦 2. Check User API Files"
echo "----------------------------"
echo "✓ User Views:"
ls -lah backend/apps/users/views.py 2>/dev/null && echo "  ✅ views.py exists" || echo "  ❌ views.py missing"

echo "✓ User Serializers:"
ls -lah backend/apps/users/serializers.py 2>/dev/null && echo "  ✅ serializers.py exists" || echo "  ❌ serializers.py missing"

echo "✓ User URLs:"
ls -lah backend/apps/users/urls.py 2>/dev/null && echo "  ✅ urls.py exists" || echo "  ❌ urls.py missing"

echo ""
echo "🔍 3. Verify Settings Integration"
echo "-----------------------------------"
grep -q "apps.core" backend/config/settings.py && echo "  ✅ Core app registered" || echo "  ❌ Core app not registered"
grep -q "apps.users.urls" backend/config/urls.py && echo "  ✅ User URLs registered" || echo "  ❌ User URLs not registered"
grep -q "TenantMiddleware" backend/config/settings.py && echo "  ✅ Tenant middleware registered" || echo "  ❌ Tenant middleware not registered"

echo ""
echo "📝 4. File Structure Summary"
echo "-----------------------------"
echo "backend/apps/core/"
ls -1 backend/apps/core/ 2>/dev/null | sed 's/^/  /'

echo ""
echo "backend/apps/users/"
ls -1 backend/apps/users/ | grep -E "(views|serializers|urls)" | sed 's/^/  /'

echo ""
echo "✅ Phase 2 File Check Complete!"
echo ""
echo "📚 Next Steps:"
echo "  1. Run migrations: docker-compose exec backend python manage.py makemigrations"
echo "  2. Apply migrations: docker-compose exec backend python manage.py migrate"
echo "  3. Test API: curl http://localhost:8001/api/users/me/"
echo "  4. Test Tenants: curl http://localhost:8001/api/tenants/me/"
echo ""
