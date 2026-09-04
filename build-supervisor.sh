#!/bin/bash
# مشرف البناء: يعيد محاولة buildozer حتى 25 مرة (كل محاولة فاشلة تحفظ ما تم تحميله)
export HOME=/home/hasan
cd /home/hasan/voice-creator || exit 1
source /home/hasan/buildozer-venv/bin/activate

for i in $(seq 1 25); do
  echo "=================== ATTEMPT $i ==================="
  buildozer -v android debug
  rc=$?
  if ls bin/*.apk >/dev/null 2>&1; then
    echo "BUILD_SUCCESS_WITH_APK"
    ls -la bin/
    exit 0
  fi
  echo "attempt $i exit=$rc, retrying in 15s..."
  sleep 15
done
echo "=== SUPERVISOR DONE (no apk) ==="
ls -la /home/hasan/voice-creator/bin/ 2>/dev/null
