# Windows Build Script for MyPDFLibrary
Write-Output "Building MyPDFLibrary for Windows..."

# 1. Clean previous builds
if (Test-Path "dist\MyPDFLibrary.exe") {
    Remove-Item "dist\MyPDFLibrary.exe" -Force
}
if (Test-Path "build") {
    Remove-Item "build" -Recurse -Force
}

# 2. Run PyInstaller
# Using python -m PyInstaller to avoid PATH issues
python -m PyInstaller MyPDFLibrary.spec --clean --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Output "Build Successful! Executable is in dist\MyPDFLibrary.exe"
} else {
    Write-Error "Build Failed!"
}
