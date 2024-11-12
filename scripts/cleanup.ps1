# Location: E:/justica/scripts/cleanup.ps1

$projectRoot = "E:/justica"

# Files to remove
$filesToRemove = @(
    "code_documentation_20241112_142854.md",
    "scripts/config/validate_config.py",
    "scripts/monitoring/validate.py",
    "scripts/services/validate_services.py",
    "scripts/setup/create_auth.py",
    "scripts/setup/create_auth.ps1",
    "scripts/setup/setup_directories.py",
    "scripts/setup/setup_permissions",
    "scripts/setup/ssl_auth.py",
    "scripts/test_cv_gpu.py",
    "scripts/utils/benchmark.py",
    "scripts/utils/generate_secrets.py"
)

# Directories to remove
$dirsToRemove = @(
    "scripts/config",
    "scripts/monitoring",
    "scripts/services",
    "scripts/setup",
    "scripts/utils",
    "tests/integration",
    "tests/performance",
    "tests/unit",
    ".github",
    "model_cache",
    "output"
)

# Function to safely remove items
function Remove-SafelyWithConfirmation {
    param (
        [string]$path,
        [string]$type
    )
    
    if (Test-Path $path) {
        Write-Host "Found $type at: $path"
        $confirmation = Read-Host "Do you want to remove it? (y/n)"
        if ($confirmation -eq 'y') {
            if ($type -eq "directory") {
                Remove-Item -Path $path -Recurse -Force
            } else {
                Remove-Item -Path $path -Force
            }
            Write-Host "Removed: $path" -ForegroundColor Green
        } else {
            Write-Host "Skipped: $path" -ForegroundColor Yellow
        }
    }
}

# Main cleanup process
Write-Host "Starting cleanup process..." -ForegroundColor Cyan

# Remove files
foreach ($file in $filesToRemove) {
    $fullPath = Join-Path $projectRoot $file
    Remove-SafelyWithConfirmation -path $fullPath -type "file"
}

# Remove directories
foreach ($dir in $dirsToRemove) {
    $fullPath = Join-Path $projectRoot $dir
    Remove-SafelyWithConfirmation -path $fullPath -type "directory"
}

# Create minimal directory structure
$dirsToCreate = @(
    "config/monitoring/grafana",
    "config/monitoring/prometheus",
    "config/services/nginx",
    "config/services/redis",
    "data/ai",
    "data/models",
    "scripts",
    "src/api",
    "src/core",
    "src/ml"
)

foreach ($dir in $dirsToCreate) {
    $fullPath = Join-Path $projectRoot $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -Path $fullPath -ItemType Directory -Force
        Write-Host "Created directory: $fullPath" -ForegroundColor Green
    }
}

Write-Host "`nCleanup completed!" -ForegroundColor Cyan
Write-Host "Next steps:"
Write-Host "1. Verify the remaining directory structure"
Write-Host "2. Run setup.py to configure the system"
Write-Host "3. Run validate.py to verify the setup"