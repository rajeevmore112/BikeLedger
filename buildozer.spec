[app]
title = BikeLedger
package.name = bikeledger
package.domain = org.rajeevmore

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,db
source.exclude_dirs = .git,.venv,venv,build,dist,backups,__pycache__

version = 0.1.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0

orientation = portrait
fullscreen = 0

android.permissions =
android.api = 35
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
