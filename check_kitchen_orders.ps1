# Kitchen Display - Database Check Script (PowerShell)
# Checks orders in database for debugging

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Kitchen Display - Database Check" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Checking all orders in database..." -ForegroundColor Yellow
Write-Host ""

# Run Python script in Docker container
Get-Content check_orders.py | docker-compose exec -T backend python manage.py shell

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Check complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan

# Keep window open
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
