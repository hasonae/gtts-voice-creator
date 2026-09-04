$ErrorActionPreference = 'Continue'
$tmp = "C:\p4a-dl"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$curl = "curl.exe"

function Get-File($url, $out, $resume = $true, $max = 40) {
  $part = "$out.part"
  for ($i = 1; $i -le $max; $i++) {
    if ((Test-Path $out) -and ((Get-Item $out).Length -gt 0)) { Write-Host "HAVE $(Split-Path $out -Leaf)"; return $true }
    $args = @('-fL', '-o', $part, '--retry', '2', '--retry-delay', '2', '--connect-timeout', '20', '-m', '1200', '-sS')
    if ($resume -and (Test-Path $part)) { $args += @('-C', '-') }
    $args += $url
    & $curl @args
    $code = $LASTEXITCODE
    if ($code -eq 0 -and (Test-Path $part) -and ((Get-Item $part).Length -gt 0)) { Move-Item -Force $part $out; Write-Host "OK   $(Split-Path $out -Leaf)"; return $true }
    if ($code -eq 33) { Remove-Item -Force $part -ErrorAction SilentlyContinue; Write-Host "NO-RANGE, restart" }
    Write-Host "RETRY($i) code=$code $(Split-Path $out -Leaf)"
    Start-Sleep 3
  }
  Write-Host "PERMANENT_FAIL $url"; return $false
}

# 1) python 3.14.2
Get-File 'https://www.python.org/ftp/python/3.14.2/Python-3.14.2.tgz' "$tmp\v3.14.2.tar.gz"

# 2) SDL2 (md5 checked by recipe -> official tarball)
if (-not (Get-File 'https://www.libsdl.org/release/SDL2-2.30.11.tar.gz' "$tmp\SDL2-2.30.11.tar.gz")) {
  Get-File 'https://github.com/libsdl-org/SDL/releases/download/release-2.30.11/SDL2-2.30.11.tar.gz' "$tmp\SDL2-2.30.11.tar.gz"
}

# 3) SDL2_image / mixer / ttf (github release assets = resumable)
Get-File 'https://github.com/libsdl-org/SDL_image/releases/download/release-2.8.2/SDL2_image-2.8.2.tar.gz' "$tmp\SDL2_image-2.8.2.tar.gz"
Get-File 'https://github.com/libsdl-org/SDL_mixer/releases/download/release-2.6.3/SDL2_mixer-2.6.3.tar.gz' "$tmp\SDL2_mixer-2.6.3.tar.gz"
Get-File 'https://github.com/libsdl-org/SDL_ttf/releases/download/release-2.22.0/SDL2_ttf-2.22.0.tar.gz' "$tmp\SDL2_ttf-2.22.0.tar.gz"

# 4) libffi (release asset first, fallback archive)
if (-not (Get-File 'https://github.com/libffi/libffi/releases/download/v3.4.2/libffi-3.4.2.tar.gz' "$tmp\v3.4.2.tar.gz")) {
  Get-File 'https://github.com/libffi/libffi/archive/v3.4.2.tar.gz' "$tmp\v3.4.2.tar.gz" -resume $false
}

# 5) sqlite3 autoconf amalgamation
Get-File 'https://www.sqlite.org/2025/sqlite-autoconf-3500400.tar.gz' "$tmp\version-3.50.4.tar.gz"

# 6) openssl
Get-File 'https://www.openssl.org/source/openssl-3.3.1.tar.gz' "$tmp\openssl-3.3.1.tar.gz"

# 7) kivy + pyjnius from PyPI -> repack as zip
$kjson = Invoke-RestMethod -Uri 'https://pypi.org/pypi/Kivy/2.3.1/json' -TimeoutSec 60
$kurl  = ($kjson.urls | Where-Object { $_.packagetype -eq 'sdist' }).url
Get-File $kurl "$tmp\Kivy-2.3.1.tar.gz" -resume $false

$pjson = Invoke-RestMethod -Uri 'https://pypi.org/pypi/pyjnius/1.7.0/json' -TimeoutSec 60
$purl  = ($pjson.urls | Where-Object { $_.packagetype -eq 'sdist' }).url
Get-File $purl "$tmp\pyjnius-1.7.0.tar.gz" -resume $false

# unpack tar.gz -> zip with top folder
New-Item -ItemType Directory -Force -Path "$tmp\zx" | Out-Null
foreach ($pair in @(@('Kivy-2.3.1.tar.gz','2.3.1.zip'), @('pyjnius-1.7.0.tar.gz','1.7.0.zip'))) {
  $tgz = "$tmp\$($pair[0])"; $zip = "$tmp\$($pair[1])"
  if ((Test-Path $tgz) -and -not (Test-Path $zip)) {
    Remove-Item -Recurse -Force "$tmp\zx\*" -ErrorAction SilentlyContinue
    & tar -xzf $tgz -C "$tmp\zx"
    $top = Get-ChildItem "$tmp\zx" | Select-Object -First 1
    Compress-Archive -Path $top.FullName -DestinationPath $zip -Force
    Write-Host "ZIPPED $zip"
  }
}

Get-ChildItem $tmp | Format-Table Name, Length -AutoSize | Out-String -Width 120
Write-Host 'DOWNLOAD_PHASE_DONE'
