$exclude = @('__pycache__', '.git', 'node_modules', '.pytest_cache', '.venv', 'venv')
$zip = 'deploy.zip'
if (Test-Path $zip) { Remove-Item $zip }
Add-Type -Assembly 'System.IO.Compression.FileSystem'
$archive = [System.IO.Compression.ZipFile]::Open($zip, 'Create')
foreach ($item in @('host.json','requirements.txt')) {
  if (Test-Path $item) {
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, $item, $item) | Out-Null
  }
}
Get-ChildItem -Recurse -File 'src' | Where-Object {
  $excluded = $false
  foreach ($ex in $exclude) { if ($_.FullName -match [regex]::Escape($ex)) { $excluded = $true; break } }
  -not $excluded -and $_.Extension -ne '.pyc'
} | ForEach-Object {
  $rel = $_.FullName.Substring((Get-Location).Path.Length + 1).Replace('\','/')
  [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, $_.FullName, $rel) | Out-Null
}
$archive.Dispose()
Write-Host "Created deploy.zip: $((Get-Item deploy.zip).Length) bytes"
