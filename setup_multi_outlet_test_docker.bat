@echo off
REM ============================================================================
REM Complete Test Data Setup Script for Docker (OPSI 2 Many-to-Many)
REM ============================================================================
REM This script sets up complete test data for the multi-store multi-outlet system:
REM - 4 Tenants: YOGYA, BORMA, MATAHARI, CARREFOUR (Retail Companies)
REM - 12 Stores: 3 per tenant (Physical retail locations)
REM - 3 Global Brands: Chicken Sumo, Magic Oven, Magic Pizza
REM - StoreOutlet junction: Links brands to stores (M2M)
REM - 9 Categories: 3 per brand
REM - 27 Products: 9 per brand
REM - Kitchen stations per brand
REM ============================================================================

echo.
echo ========================================================================
echo OPSI 2 MANY-TO-MANY TEST DATA SETUP (DOCKER)
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

echo [1/1] Setting up complete test data (Many-to-Many Architecture)...
echo.
docker-compose exec backend python setup_complete_test_data.py
if errorlevel 1 (
    echo.
    echo ❌ Failed to setup test data!
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo ✅ ALL TEST DATA SETUP COMPLETED!
echo ========================================================================
echo.
echo You now have:
echo   - 4 Tenants (YOGYA, BORMA, MATAHARI, CARREFOUR)
echo   - 12 Stores (3 per tenant with operating hours)
echo   - 3 Global Brands (Chicken Sumo, Magic Oven, Magic Pizza)
echo   - 30 Store-Brand Assignments (Many-to-Many)
echo   - 6 Kitchen Stations (2 per brand)
echo   - 9 Categories (3 per brand)
echo   - 27 Products (9 per brand)
echo.
echo 🎉 Ready to test the OPSI 2 Many-to-Many system!
echo 🔗 Test Store Code: YOGYA-KAPATIHAN
echo 🔗 Access admin panel at: http://localhost:5175/
echo.
pause
