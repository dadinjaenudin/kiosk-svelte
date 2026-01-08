# Test Kitchen Display HTTP Polling
# This script verifies the kitchen display polling mechanism

Write-Host "🧪 Testing Kitchen Display HTTP Polling" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$API_BASE = "http://localhost:8001/api"
$OUTLET_ID = 519
$TEST_CYCLES = 3

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "  API Base: $API_BASE"
Write-Host "  Outlet ID: $OUTLET_ID"
Write-Host "  Test Cycles: $TEST_CYCLES"
Write-Host ""

# Test 1: Check API endpoints
Write-Host "Test 1: Checking Kitchen API Endpoints..." -ForegroundColor Green

try {
    $pending = Invoke-RestMethod -Uri "$API_BASE/kitchen/orders/pending/?outlet=$OUTLET_ID" -Method Get
    $preparing = Invoke-RestMethod -Uri "$API_BASE/kitchen/orders/preparing/?outlet=$OUTLET_ID" -Method Get
    $ready = Invoke-RestMethod -Uri "$API_BASE/kitchen/orders/ready/?outlet=$OUTLET_ID" -Method Get
    $stats = Invoke-RestMethod -Uri "$API_BASE/kitchen/orders/stats/?outlet=$OUTLET_ID" -Method Get
    
    Write-Host "  ✅ Pending endpoint: OK ($($pending.Count) orders)" -ForegroundColor Green
    Write-Host "  ✅ Preparing endpoint: OK ($($preparing.Count) orders)" -ForegroundColor Green
    Write-Host "  ✅ Ready endpoint: OK ($($ready.Count) orders)" -ForegroundColor Green
    Write-Host "  ✅ Stats endpoint: OK" -ForegroundColor Green
    Write-Host ""
    
    # Display stats
    Write-Host "📊 Current Statistics:" -ForegroundColor Yellow
    Write-Host "  Pending: $($stats.pending_count)"
    Write-Host "  Preparing: $($stats.preparing_count)"
    Write-Host "  Ready: $($stats.ready_count)"
    Write-Host "  Completed Today: $($stats.completed_today)"
    Write-Host "  Avg Prep Time: $($stats.avg_prep_time) min"
    Write-Host ""
    
} catch {
    Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Simulate polling cycles
Write-Host "Test 2: Simulating Polling Cycles (10s interval)..." -ForegroundColor Green

for ($i = 1; $i -le $TEST_CYCLES; $i++) {
    Write-Host "  Cycle $i/$TEST_CYCLES..." -ForegroundColor Cyan
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    try {
        $pending = Invoke-RestMethod -Uri "$API_BASE/kitchen/orders/pending/?outlet=$OUTLET_ID" -Method Get
        $stats = Invoke-RestMethod -Uri "$API_BASE/kitchen/orders/stats/?outlet=$OUTLET_ID" -Method Get
        
        Write-Host "    [$timestamp] Pending: $($pending.Count) | Preparing: $($stats.preparing_count) | Ready: $($stats.ready_count)" -ForegroundColor White
        
    } catch {
        Write-Host "    ❌ Polling failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    if ($i -lt $TEST_CYCLES) {
        Write-Host "    ⏳ Waiting 10 seconds..." -ForegroundColor Gray
        Start-Sleep -Seconds 10
    }
}
Write-Host ""

# Test 3: Check order details
if ($pending.Count -gt 0) {
    Write-Host "Test 3: Checking Order Details..." -ForegroundColor Green
    
    $order = $pending[0]
    Write-Host "  Order Number: $($order.order_number)" -ForegroundColor White
    Write-Host "  Status: $($order.status)" -ForegroundColor White
    Write-Host "  Wait Time: $($order.wait_time) min" -ForegroundColor White
    Write-Host "  Is Urgent: $($order.is_urgent)" -ForegroundColor $(if ($order.is_urgent) { "Red" } else { "Green" })
    Write-Host "  Customer: $($order.customer_name)" -ForegroundColor White
    Write-Host "  Items: $($order.items.Count)" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "Test 3: No pending orders to check" -ForegroundColor Yellow
    Write-Host ""
}

# Test 4: Frontend accessibility
Write-Host "Test 4: Checking Frontend Accessibility..." -ForegroundColor Green

try {
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:5174/kitchen/login" -UseBasicParsing
    $displayResponse = Invoke-WebRequest -Uri "http://localhost:5174/kitchen/display" -UseBasicParsing
    
    Write-Host "  ✅ Kitchen Login: $($loginResponse.StatusCode)" -ForegroundColor Green
    Write-Host "  ✅ Kitchen Display: $($displayResponse.StatusCode)" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "  ❌ Frontend error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Kitchen Display Polling Test Complete" -ForegroundColor Green
Write-Host ""
Write-Host "📌 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open Kitchen Display: http://localhost:5174/kitchen/login"
Write-Host "  2. Select store and outlet"
Write-Host "  3. Watch orders update every 10 seconds"
Write-Host "  4. Create order from kiosk to test real-time flow"
Write-Host ""
Write-Host "🔜 Future Enhancement: Socket.IO real-time (Phase 3.3)" -ForegroundColor Cyan
Write-Host ""
