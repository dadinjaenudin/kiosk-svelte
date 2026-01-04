# Kitchen Sync Server - Install Auto-Start
# Run this script as Administrator

param(
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   KITCHEN SYNC SERVER - AUTO-START INSTALLER" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Check for admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run PowerShell as Administrator and try again:" -ForegroundColor Yellow
    Write-Host "  Right-click PowerShell -> Run as Administrator" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startScript = Join-Path $scriptDir "START_KITCHEN_SYNC.bat"
$serverJs = Join-Path $scriptDir "server.js"
$taskName = "Kitchen Sync Server"

# Uninstall mode
if ($Uninstall) {
    Write-Host "Removing auto-start task..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($task) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
            Write-Host "========================================================" -ForegroundColor Green
            Write-Host "   AUTO-START REMOVED SUCCESSFULLY!" -ForegroundColor Green
            Write-Host "========================================================" -ForegroundColor Green
            Write-Host ""
        } else {
            Write-Host "[INFO] Auto-start task not found. Nothing to remove." -ForegroundColor Yellow
            Write-Host ""
        }
    } catch {
        Write-Host "[ERROR] Failed to remove task: $_" -ForegroundColor Red
        Write-Host ""
    }
    
    Read-Host "Press Enter to exit"
    exit 0
}

# Check if Node.js is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version 2>$null
    Write-Host "[OK] Node.js is installed: $nodeVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERROR] Node.js is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Node.js first:" -ForegroundColor Yellow
    Write-Host "  Download from: https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if server.js exists
if (-not (Test-Path $serverJs)) {
    Write-Host "[ERROR] server.js not found at:" -ForegroundColor Red
    Write-Host "  $serverJs" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] server.js found" -ForegroundColor Green
Write-Host ""

# Check if START_KITCHEN_SYNC.bat exists
if (-not (Test-Path $startScript)) {
    Write-Host "[ERROR] START_KITCHEN_SYNC.bat not found at:" -ForegroundColor Red
    Write-Host "  $startScript" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] START_KITCHEN_SYNC.bat found" -ForegroundColor Green
Write-Host ""

# Check if node_modules exists
$nodeModules = Join-Path $scriptDir "node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Host "[WARNING] node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    Write-Host ""
    
    Push-Location $scriptDir
    try {
        npm install
        if ($LASTEXITCODE -ne 0) {
            throw "npm install failed"
        }
        Write-Host ""
        Write-Host "[OK] Dependencies installed" -ForegroundColor Green
        Write-Host ""
    } catch {
        Write-Host "[ERROR] Failed to install dependencies: $_" -ForegroundColor Red
        Write-Host ""
        Pop-Location
        Read-Host "Press Enter to exit"
        exit 1
    }
    Pop-Location
}

# Create scheduled task
Write-Host "Creating Windows Task Scheduler entry..." -ForegroundColor Cyan
Write-Host ""

try {
    # Remove existing task if exists
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "[INFO] Removing existing task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    
    # Create action
    $action = New-ScheduledTaskAction -Execute $startScript -WorkingDirectory $scriptDir
    
    # Create trigger (at logon)
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    
    # Create principal (run with highest privileges)
    $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -RunLevel Highest -LogonType Interactive
    
    # Create settings
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
    
    # Register task
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Kitchen Sync Server for POS real-time communication" | Out-Null
    
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host "   AUTO-START INSTALLED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "The Kitchen Sync Server will now start automatically" -ForegroundColor Green
    Write-Host "when you log in to Windows." -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name:        $taskName" -ForegroundColor White
    Write-Host "  Trigger:     At user logon" -ForegroundColor White
    Write-Host "  Script:      $startScript" -ForegroundColor White
    Write-Host "  Run Level:   Highest (Administrator)" -ForegroundColor White
    Write-Host ""
    Write-Host "Management Commands:" -ForegroundColor Cyan
    Write-Host "  Test now:    .\START_KITCHEN_SYNC.bat" -ForegroundColor Yellow
    Write-Host "  View task:   Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
    Write-Host "  Uninstall:   .\INSTALL_AUTOSTART.ps1 -Uninstall" -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "[ERROR] Failed to create scheduled task!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"
