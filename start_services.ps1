# PowerShell script to start all services with enhanced cancellation support
# For the graduation project with LangSmith graph cancellation

# Function to cleanup on exit
function Cleanup {
    Write-Host "Shutting down services gracefully..." -ForegroundColor Yellow
    
    try {
        # Cancel all Celery tasks and graph executions
        Write-Host "Cancelling all Celery tasks and graph executions..." -ForegroundColor Yellow
        python manage.py control_tasks cancel-all
        
        # Stop Celery workers gracefully
        Write-Host "Stopping Celery workers..." -ForegroundColor Yellow
        celery -A graduation_backend control shutdown
        
        # Purge Redis queues
        Write-Host "Clearing Redis queues..." -ForegroundColor Yellow
        redis-cli flushdb
        
        # Stop Redis server
        Write-Host "Stopping Redis server..." -ForegroundColor Yellow
        redis-cli shutdown
        
        Write-Host "All services stopped successfully!" -ForegroundColor Green
        
    } catch {
        Write-Host "Error during shutdown: $_" -ForegroundColor Red
    }
    
    exit 0
}

# Set up signal handlers
trap Cleanup INT TERM

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# Function to wait for a service to be ready
function Wait-ForService {
    param([int]$Port, [string]$ServiceName, [int]$Timeout = 30)
    
    Write-Host "Waiting for $ServiceName to be ready on port $Port..." -ForegroundColor Cyan
    $startTime = Get-Date
    $timeoutSpan = [TimeSpan]::FromSeconds($Timeout)
    
    while ((Get-Date) - $startTime -lt $timeoutSpan) {
        if (Test-Port -Port $Port) {
            Write-Host "$ServiceName is ready!" -ForegroundColor Green
            return $true
        }
        Start-Sleep -Seconds 1
    }
    
    Write-Host "$ServiceName failed to start within $Timeout seconds" -ForegroundColor Red
    return $false
}

# Function to start Redis
function Start-Redis {
    Write-Host "Starting Redis server..." -ForegroundColor Cyan
    
    # Check if Redis is already running
    if (Test-Port -Port 6379) {
        Write-Host "Redis is already running on port 6379" -ForegroundColor Yellow
        return $true
    }
    
    try {
        # Try to start Redis using different methods
        $redisProcess = $null
        
        # Method 1: Try to start redis-server directly
        try {
            $redisProcess = Start-Process -FilePath "redis-server" -ArgumentList "--port", "6379" -WindowStyle Hidden -PassThru
            Write-Host "Redis started using redis-server command" -ForegroundColor Green
        } catch {
            # Method 2: Try to start using WSL if available
            try {
                $redisProcess = Start-Process -FilePath "wsl" -ArgumentList "redis-server", "--port", "6379" -WindowStyle Hidden -PassThru
                Write-Host "Redis started using WSL" -ForegroundColor Green
            } catch {
                # Method 3: Try to start using Docker if available
                try {
                    $redisProcess = Start-Process -FilePath "docker" -ArgumentList "run", "-d", "--name", "redis", "-p", "6379:6379", "redis:latest" -WindowStyle Hidden -PassThru
                    Write-Host "Redis started using Docker" -ForegroundColor Green
                } catch {
                    throw "Could not start Redis using any available method"
                }
            }
        }
        
        # Wait for Redis to be ready
        if (Wait-ForService -Port 6379 -ServiceName "Redis" -Timeout 10) {
            return $true
        } else {
            throw "Redis failed to start"
        }
        
    } catch {
        Write-Host "Failed to start Redis: $_" -ForegroundColor Red
        Write-Host "Please ensure Redis is installed and available in your PATH" -ForegroundColor Yellow
        Write-Host "Or install Redis using one of these methods:" -ForegroundColor Yellow
        Write-Host "  - Windows: Download from https://redis.io/download" -ForegroundColor Yellow
        Write-Host "  - WSL: sudo apt-get install redis-server" -ForegroundColor Yellow
        Write-Host "  - Docker: docker run -d --name redis -p 6379:6379 redis:latest" -ForegroundColor Yellow
        return $false
    }
}

# Function to start Celery worker
function Start-Celery {
    Write-Host "Starting Celery worker..." -ForegroundColor Cyan
    
    try {
        # Start Celery worker with enhanced configuration
        $celeryArgs = @(
            "-A", "graduation_backend",
            "worker",
            "--loglevel=info",
            "--pool=prefork",
            "--concurrency=2",
            "--queues=ai_processing,email,default"
        )
        
        $celeryProcess = Start-Process -FilePath "celery" -ArgumentList $celeryArgs -WindowStyle Hidden -PassThru
        Write-Host "Celery worker started successfully" -ForegroundColor Green
        return $celeryProcess
        
    } catch {
        Write-Host "Failed to start Celery worker: $_" -ForegroundColor Red
        Write-Host "Please ensure Celery is installed: pip install celery" -ForegroundColor Yellow
        return $null
    }
}

# Function to start Daphne server
function Start-Daphne {
    Write-Host "Starting Daphne server..." -ForegroundColor Cyan
    
    try {
        # Start Daphne server with enhanced configuration
        $daphneArgs = @(
            "-b", "0.0.0.0",
            "-p", "8000",
            "graduation_backend.asgi:application"
        )
        
        $daphneProcess = Start-Process -FilePath "daphne" -ArgumentList $daphneArgs -WindowStyle Normal -PassThru
        Write-Host "Daphne server started successfully on port 8000" -ForegroundColor Green
        return $daphneProcess
        
    } catch {
        Write-Host "Failed to start Daphne server: $_" -ForegroundColor Red
        Write-Host "Please ensure Daphne is installed: pip install daphne" -ForegroundColor Yellow
        return $null
    }
}

# Main execution
Write-Host "Starting Graduation Project Services with Enhanced Cancellation Support" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host ""

# Check if we're in the project directory
if (-not (Test-Path "manage.py")) {
    Write-Host "Error: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Expected: Directory containing manage.py" -ForegroundColor Yellow
    exit 1
}

Write-Host "Project directory: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Step 1: Start Redis
if (-not (Start-Redis)) {
    Write-Host "Failed to start Redis. Exiting." -ForegroundColor Red
    exit 1
}

# Step 2: Start Celery worker
$celeryProcess = Start-Celery
if (-not $celeryProcess) {
    Write-Host "Failed to start Celery worker. Exiting." -ForegroundColor Red
    exit 1
}

# Wait a moment for Celery to initialize
Start-Sleep -Seconds 3

# Step 3: Start Daphne server
$daphneProcess = Start-Daphne
if (-not $daphneProcess) {
    Write-Host "Failed to start Daphne server. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "All services started successfully!" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "Redis: Running on port 6379" -ForegroundColor Cyan
Write-Host "Celery: Worker running with enhanced cancellation support" -ForegroundColor Cyan
Write-Host "Daphne: Server running on http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop all services, press Ctrl+C" -ForegroundColor Yellow
Write-Host "Or use: python manage.py control_tasks cancel-all" -ForegroundColor Yellow
Write-Host ""

# Wait for Daphne process to complete (this will keep the script running)
try {
    $daphneProcess.WaitForExit()
} catch {
    Write-Host "Daphne server stopped unexpectedly" -ForegroundColor Yellow
}

# If we get here, cleanup and exit
Cleanup
