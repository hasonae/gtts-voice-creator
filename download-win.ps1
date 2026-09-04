$ErrorActionPreference = 'Continue'
$tmp = "$env:TEMP\p4a-src"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

$items = @(
  @{ url='https://github.com/python/cpython/archive/refs/tags/v3.14.2.tar.gz'; file='v3.14.2.tar.gz' },
  @{ url='https://github.com/kivy/kivy/archive/2.3.1.zip'; file='2.3.1.zip' },
  @{ url='https://github.com/kivy/pyjnius/archive/1.7.0.zip'; file='1.7.0.zip' },
  @{ url='https://github.com/libsdl-org/SDL/releases/download/release-2.30.11/SDL2-2.30.11.tar.gz'; file='SDL2-2.30.11.tar.gz' },
  @{ url='https://github.com/libsdl-org/SDL_image/releases/download/release-2.8.2/SDL2_image-2.8.2.tar.gz'; file='SDL2_image-2.8.2.tar.gz' },
  @{ url='https://github.com/libsdl-org/SDL_mixer/releases/download/release-2.6.3/SDL2_mixer-2.6.3.tar.gz'; file='SDL2_mixer-2.6.3.tar.gz' },
  @{ url='https://github.com/libsdl-org/SDL_ttf/releases/download/release-2.22.0/SDL2_ttf-2.22.0.tar.gz'; file='SDL2_ttf-2.22.0.tar.gz' },
  @{ url='https://github.com/libffi/libffi/archive/v3.4.2.tar.gz'; file='v3.4.2.tar.gz' },
  @{ url='https://github.com/sqlite/sqlite/archive/refs/tags/version-3.50.4.tar.gz'; file='version-3.50.4.tar.gz' },
  @{ url='https://www.openssl.org/source/openssl-3.3.1.tar.gz'; file='openssl-3.3.1.tar.gz' }
)

foreach ($it in $items) {
  $dest = Join-Path $tmp $it.file
  if (Test-Path $dest) { Write-Host "HAVE $($it.file)"; continue }
  $ok = $false
  for ($i = 1; $i -le 8; $i++) {
    try {
      Write-Host "GET($i) $($it.file)..."
      Invoke-WebRequest -Uri $it.url -OutFile "$dest.part" -TimeoutSec 900 -UseBasicParsing
      Move-Item -Force "$dest.part" $dest
      $ok = $true; break
    } catch { Write-Host "FAIL($i): $($_.Exception.Message)"; Start-Sleep 5 }
  }
  if (-not $ok) { Write-Host "PERMANENT_FAIL $($it.file)" }
}
Get-ChildItem $tmp | Format-Table Name, Length -AutoSize
