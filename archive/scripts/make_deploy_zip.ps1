# Build a deployment zip matching the GitHub Actions workflow structure:
# - Function dirs staged at root (format_exam/, serve_web/, upload_syllabus/, etc.)
# - src/ staged at root (for "from src.agents..." imports)
# - web/ staged at root (serve_web fallback path)
# - .python_packages/lib/site-packages/ with installed deps

param([switch]$SkipPip)

$Root = Get-Location
$DeployDir = Join-Path $Root '_deploy_staging'
$ZipPath = Join-Path $Root 'deploy.zip'

# Clean staging dir
if (Test-Path $DeployDir) { Remove-Item -Recurse -Force $DeployDir }
New-Item -ItemType Directory -Path $DeployDir | Out-Null

Write-Host "Staging deployment files..."

# 1. host.json + requirements.txt
Copy-Item 'host.json'       (Join-Path $DeployDir 'host.json')
Copy-Item 'requirements.txt' (Join-Path $DeployDir 'requirements.txt')

# 2. Stage ALL function dirs at root (Azure Functions v1 model discovers them here)
$funcSrc = Join-Path $Root 'src\functions'
Get-ChildItem $funcSrc -Directory | ForEach-Object {
    $dest = Join-Path $DeployDir $_.Name
    Copy-Item $_.FullName $dest -Recurse
    Write-Host "  + Function: $($_.Name)"
}

# 3. Stage src/ at root (for "from src.agents..." imports)
$srcDest = Join-Path $DeployDir 'src'
Copy-Item (Join-Path $Root 'src') $srcDest -Recurse -Exclude @('__pycache__','*.pyc')

# 4. Stage web/ at root (serve_web fallback path)
$webDest = Join-Path $DeployDir 'web'
Copy-Item (Join-Path $Root 'src\web') $webDest -Recurse

# 5. Install Python packages into .python_packages
if (-not $SkipPip) {
    Write-Host "Installing Python packages (this may take a minute)..."
    $pkgDir = Join-Path $DeployDir '.python_packages\lib\site-packages'
    New-Item -ItemType Directory -Path $pkgDir -Force | Out-Null
    pip install -r requirements.txt --target $pkgDir --quiet 2>&1 | Out-Null
    Write-Host "  Packages installed."
}

# 6. Remove __pycache__ and .pyc files from staging
Write-Host "Cleaning up pyc files..."
Get-ChildItem -Recurse -Path $DeployDir -Include '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Path $DeployDir -Include '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue

# 7. Zip it
Write-Host "Creating deploy.zip..."
if (Test-Path $ZipPath) { Remove-Item $ZipPath }
Add-Type -Assembly 'System.IO.Compression.FileSystem'
[System.IO.Compression.ZipFile]::CreateFromDirectory($DeployDir, $ZipPath)

$sizeMB = [math]::Round((Get-Item $ZipPath).Length / 1MB, 1)
Write-Host "Created deploy.zip: ${sizeMB} MB"

# Cleanup
Remove-Item -Recurse -Force $DeployDir
Write-Host "Done."
