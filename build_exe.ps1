$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "[1/4] Instalando dependencias..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

Write-Host "[2/4] Limpiando artefactos anteriores..."
Remove-Item -Recurse -Force build, dist, AlbertTranslator.spec -ErrorAction SilentlyContinue

Write-Host "[3/4] Generando ejecutable en un solo archivo..."
python -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name AlbertTranslator `
  --add-data "templates;templates" `
  --add-data "static;static" `
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

Write-Host "[4/4] Creando carpeta portable..."
$portableDir = Join-Path $projectRoot "dist\portable"
New-Item -ItemType Directory -Force -Path $portableDir | Out-Null
$portableExe = Join-Path $portableDir "AlbertTranslator.exe"
try {
  Copy-Item "dist\AlbertTranslator.exe" $portableExe -Force
}
catch {
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $fallbackExe = Join-Path $portableDir "AlbertTranslator_$stamp.exe"
  Copy-Item "dist\AlbertTranslator.exe" $fallbackExe -Force
  Write-Warning "AlbertTranslator.exe estaba bloqueado. Se guardo como: $fallbackExe"
}
Copy-Item ".env.example" (Join-Path $portableDir ".env.example") -Force

@'
1) Renombra ".env.example" a ".env"
2) Ejecuta AlbertTranslator.exe
3) Haz clic en "Guardar config" y luego en "Iniciar servidor"
4) Si el navegador no abre solo, haz clic en "Abrir web"
5) Permite microfono en el navegador (Chrome/Edge recomendado)
6) Si se cierra o falla la conexion, revisa "alberttranslator.log" junto al exe
'@ | Set-Content -Encoding ASCII (Join-Path $portableDir "LEEME_PORTABLE.txt")

Write-Host "Build portable listo en: $portableDir"
