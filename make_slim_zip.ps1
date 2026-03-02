# Build a SLIM deployment zip (no Python packages — Azure builds them remotely)
$Root = Get-Location
$DeployDir = Join-Path $Root '_deploy_slim'
$ZipPath = Join-Path $Root 'deploy_slim.zip'

if (Test-Path $DeployDir) { Remove-Item -Recurse -Force $DeployDir }
New-Item -ItemType Directory -Path $DeployDir | Out-Null

Write-Host "Staging slim deployment..."

Copy-Item 'host.json'        (Join-Path $DeployDir 'host.json')
Copy-Item 'requirements.txt' (Join-Path $DeployDir 'requirements.txt')

# Stage function dirs at root
$funcSrc = Join-Path $Root 'src\functions'
Get-ChildItem $funcSrc -Directory | ForEach-Object {
    $dest = Join-Path $DeployDir $_.Name
    Copy-Item $_.FullName $dest -Recurse
    Write-Host "  + $($_.Name)"
}

# Stage src/ for imports
$srcDest = Join-Path $DeployDir 'src'
New-Item -ItemType Directory -Path $srcDest | Out-Null
Get-ChildItem -Recurse -File 'src' | Where-Object {
    $_.Extension -ne '.pyc' -and $_.FullName -notmatch '__pycache__'
} | ForEach-Object {
    $rel = $_.FullName.Substring((Get-Location).Path.Length + 1)
    $destFile = Join-Path $DeployDir $rel
    $destDir = Split-Path $destFile -Parent
    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
    Copy-Item $_.FullName $destFile
}

# Stage web/ at root
$webDest = Join-Path $DeployDir 'web'
Copy-Item (Join-Path $Root 'src\web') $webDest -Recurse

if (Test-Path $ZipPath) { Remove-Item $ZipPath }
Add-Type -Assembly 'System.IO.Compression.FileSystem'
[System.IO.Compression.ZipFile]::CreateFromDirectory($DeployDir, $ZipPath)

$sizeKB = [math]::Round((Get-Item $ZipPath).Length / 1KB, 0)
Write-Host "Created deploy_slim.zip: ${sizeKB} KB"

Remove-Item -Recurse -Force $DeployDir
Write-Host "Done."
