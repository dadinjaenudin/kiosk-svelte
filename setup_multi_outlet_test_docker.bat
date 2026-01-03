@echo off
REM ============================================================================
REM Multi-Outlet Test Data Setup Script for Docker
REM ============================================================================
REM This script sets up complete test data for the food court system:
REM - Phase 1-5: Basic multi-outlet setup (tenants, outlets, categories, products, users)
REM - Complete data: Toppings, Additions, Customers, Orders
REM ============================================================================

echo.
echo ========================================================================
echo MULTI-OUTLET TEST DATA SETUP (DOCKER)
echo ========================================================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if containers are running
docker-compose ps | findstr "backend" >nul
if errorlevel 1 (
    echo ⚠️  Backend container not running. Starting containers...
    docker-compose up -d
    echo ⏳ Waiting for services to be ready...
    timeout /t 5 /nobreak >nul
)

echo [1/2] Setting up basic multi-outlet data (Phase 1-5)...
echo.
docker-compose exec backend python setup_multi_outlet_test_data.py
if errorlevel 1 (
    echo.
    echo ❌ Failed to setup basic multi-outlet data!
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo [2/2] Setting up complete test data (Toppings, Additions, Customers, Orders)...
echo.
docker-compose exec backend python setup_complete_test_data.py
if errorlevel 1 (
    echo.
    echo ❌ Failed to setup complete test data!
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo ✅ ALL TEST DATA SETUP COMPLETED!
echo ========================================================================
echo.
echo You now have:
echo   - 3 Tenants (Pizza Paradise, Burger Station, Noodle House)
echo   - 6 Outlets (2 per tenant)
echo   - 12 Categories
echo   - 30 Products
echo   - 20 Toppings
echo   - 15 Additions
echo   - 20 Users (with various roles)
echo   - 30 Customers
echo   - 50+ Orders (last 7 days)
echo.
echo 🎉 Ready to test the system!
echo 🔗 Access admin panel at: http://localhost:5175/
echo.
pause
