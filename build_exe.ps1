param(
    # Permite usar otro interprete si el desarrollador trabaja con un Python distinto.
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Resuelve rutas base una sola vez para no repetir logica y evitar errores de path.
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$appFile = Join-Path $projectRoot "app.py"
$iconFile = Join-Path $projectRoot "AlbertTranslator.ico"
$templatesDir = Join-Path $projectRoot "templates"
$staticDir = Join-Path $projectRoot "static"
$versionFile = Join-Path $projectRoot "VERSION"
$releaseDir = Join-Path $projectRoot "release-artifacts"
$packageDir = Join-Path $releaseDir "package"
$buildWorkDir = Join-Path $projectRoot "build\pyinstaller"
$specWorkDir = Join-Path $projectRoot "build\spec"
$rootExe = Join-Path $projectRoot "AlbertTranslator.exe"

Set-Location $projectRoot

# Valida prerequisitos obligatorios antes de gastar tiempo instalando dependencias.
if (-not (Test-Path $appFile)) {
    throw "No se encontro app.py en $projectRoot"
}

if (-not (Test-Path $iconFile)) {
    throw "No se encontro AlbertTranslator.ico en $projectRoot"
}

if (-not (Test-Path $templatesDir)) {
    throw "No se encontro templates en $projectRoot"
}

if (-not (Test-Path $staticDir)) {
    throw "No se encontro static en $projectRoot"
}

if (-not (Test-Path $versionFile)) {
    throw "No se encontro VERSION en $projectRoot"
}

$version = (Get-Content $versionFile -Raw).Trim()
if ($version -notmatch '^V\d+\.\d+\.\d+$') {
    throw "VERSION invalida: $version"
}

$versionedExe = Join-Path $releaseDir ("AlbertTranslator-{0}.exe" -f $version)
$versionedZip = Join-Path $releaseDir ("AlbertTranslator-{0}-win64.zip" -f $version)

Write-Host "[1/5] Instalando dependencias de compilacion..."
& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install -r requirements-dev.txt

Write-Host "[2/5] Limpiando artefactos generados..."
Remove-Item -Recurse -Force $buildWorkDir, $specWorkDir, $releaseDir -ErrorAction SilentlyContinue
Remove-Item -Force $rootExe -ErrorAction SilentlyContinue

Write-Host "[3/5] Generando ejecutable junto a app.py..."
& $PythonExe -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name AlbertTranslator `
  --icon $iconFile `
  --distpath $projectRoot `
  --workpath $buildWorkDir `
  --specpath $specWorkDir `
  --add-data "${templatesDir};templates" `
  --add-data "${staticDir};static" `
  --collect-all faster_whisper `
  --collect-all ctranslate2 `
  --collect-all sentencepiece `
  --collect-all huggingface_hub `
  --collect-all tokenizers `
  --exclude-module argostranslate `
  --exclude-module torch `
  --exclude-module torchvision `
  --exclude-module torchaudio `
  --exclude-module onnxruntime `
  --exclude-module minisbd `
  --exclude-module stanza `
  --exclude-module spacy `
  --exclude-module tensorflow `
  --hidden-import faster_whisper `
  --hidden-import deep_translator `
  --hidden-import langdetect `
  --hidden-import speech_recognition `
  app.py

if (-not (Test-Path $rootExe)) {
    throw "PyInstaller termino sin generar AlbertTranslator.exe"
}

Write-Host "[4/5] Preparando artefactos versionados para release..."
New-Item -ItemType Directory -Force -Path $releaseDir, $packageDir | Out-Null
Copy-Item $rootExe $versionedExe -Force
Copy-Item $rootExe (Join-Path $packageDir "AlbertTranslator.exe") -Force
Copy-Item ".env.example" (Join-Path $packageDir ".env.example") -Force

@'
1) Renombra ".env.example" a ".env"
2) Ejecuta AlbertTranslator.exe
3) Haz clic en "Guardar config" y luego en "Iniciar servidor"
4) Si el navegador no abre solo, usa "Abrir web"
5) Permite microfono en el navegador
6) Si algo falla, revisa alberttranslator.log
'@ | Set-Content -Encoding UTF8 (Join-Path $packageDir "LEEME_PORTABLE.txt")

if (Test-Path $versionedZip) {
    Remove-Item -Force $versionedZip
}
Compress-Archive -Path (Join-Path $packageDir "*") -DestinationPath $versionedZip -Force

Write-Host "[5/5] Build finalizado."
Write-Host "EXE local: $rootExe"
Write-Host "EXE versionado: $versionedExe"
Write-Host "ZIP release: $versionedZip"
