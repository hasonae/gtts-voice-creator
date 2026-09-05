[app]
title = GTTS Voice Creator
package.name = gttsvoicecreator
package.domain = org.hasanibrahem
source.dir = .
source.include_exts = py,png
version = 1.0
# تم تثبيت النسخ لتتوافق مع نسخ التطوير على الويندوز،
# و python-bidi == 0.4.2 (نسخة Python خالصة تعمل على أندرويد، النسخ الحديثة Rust لن تُبنى)
requirements = python3,kivy==2.3.1,kivymd==2.0.0,gTTS==2.5.4,arabic_reshaper==3.0.1,python-bidi==0.4.2,requests
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/gttst.png

# The app contacts Google Translate through gTTS.
android.permissions = INTERNET

# شاشة البداية عند فتح التطبيق
presplash.filename = %(source.dir)s/gttst.png

# واجهة برمجة التطبيقات وأدوات البناء
android.api = 35
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 35.0.0
android.archs = arm64-v8a
android.accept_sdk_license = True

# إظهار أخطاء Python على وحدة التحكم أثناء الاختبار (عيّنها إلى 0 عند النشر)
android.logcat_on_failure = 1

[buildozer]
log_level = 2
warn_on_root = 1