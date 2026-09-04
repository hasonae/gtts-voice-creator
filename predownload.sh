#!/bin/bash
# تحميل مسبق لأرشيفات مصادر الوصفات إلى كاش buildozer مع إعادة محاولة
export HOME=/home/hasan
CACHE=/home/hasan/.buildozer/packages
mkdir -p "$CACHE"/{python3,hostpython3,kivy,pyjnius,sdl2,sdl2_image,sdl2_mixer,sdl2_ttf,libffi,openssl,sqlite3}

dl() {
  local url="$1" dest="$2" i
  for i in $(seq 1 40); do
    if [ -s "$dest" ]; then echo "HAVE $(basename "$dest")"; return 0; fi
    if curl -fsSL --retry 3 --retry-delay 2 -m 900 -o "$dest.part" "$url"; then
      mv "$dest.part" "$dest"; echo "OK   $(basename "$dest")"; return 0
    fi
    rm -f "$dest.part"; echo "RETRY($i) $(basename "$dest")"; sleep 4
  done
  echo "FAIL $url"; return 1
}

dl "https://github.com/python/cpython/archive/refs/tags/v3.14.2.tar.gz" "$CACHE/python3/v3.14.2.tar.gz"
if [ -s "$CACHE/python3/v3.14.2.tar.gz" ]; then
  cp -n "$CACHE/python3/v3.14.2.tar.gz" "$CACHE/hostpython3/v3.14.2.tar.gz"
fi
dl "https://github.com/kivy/kivy/archive/2.3.1.zip"                                   "$CACHE/kivy/2.3.1.zip"
dl "https://github.com/kivy/pyjnius/archive/1.7.0.zip"                               "$CACHE/pyjnius/1.7.0.zip"
dl "https://github.com/libsdl-org/SDL/releases/download/release-2.30.11/SDL2-2.30.11.tar.gz"       "$CACHE/sdl2/SDL2-2.30.11.tar.gz"
dl "https://github.com/libsdl-org/SDL_image/releases/download/release-2.8.2/SDL2_image-2.8.2.tar.gz" "$CACHE/sdl2_image/SDL2_image-2.8.2.tar.gz"
dl "https://github.com/libsdl-org/SDL_mixer/releases/download/release-2.6.3/SDL2_mixer-2.6.3.tar.gz" "$CACHE/sdl2_mixer/SDL2_mixer-2.6.3.tar.gz"
dl "https://github.com/libsdl-org/SDL_ttf/releases/download/release-2.22.0/SDL2_ttf-2.22.0.tar.gz"   "$CACHE/sdl2_ttf/SDL2_ttf-2.22.0.tar.gz"
dl "https://github.com/libffi/libffi/archive/v3.4.2.tar.gz"                          "$CACHE/libffi/v3.4.2.tar.gz"
dl "https://github.com/sqlite/sqlite/archive/refs/tags/version-3.50.4.tar.gz"        "$CACHE/sqlite3/version-3.50.4.tar.gz"
dl "https://www.openssl.org/source/openssl-3.3.1.tar.gz"                             "$CACHE/openssl/openssl-3.3.1.tar.gz"

echo "=== PRE-DOWNLOAD DONE ==="
ls -laR "$CACHE" | head -60
