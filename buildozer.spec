[app]
title = 女书知识学习app
package.name = nvshuapp
package.domain = org.kivy
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,ttf,json,atlas
source.exclude_dirs = tests,scripts,artifacts,dist,bin,.venv,screenshots,state
source.exclude_patterns = data/progress/*
version = 0.2.0
requirements = python3,kivy==2.3.1
icon.filename = assets/banner.png
orientation = portrait
fullscreen = 0
android.api = 31
android.minapi = 21
android.ndk = 28c
android.ndk_api = 21
android.accept_sdk_license = True
android.enable_androidx = True
android.copy_libs = 1
android.archs = arm64-v8a, armeabi-v7a
android.numeric_version = 10212
android.allow_backup = True
android.debug_artifact = apk
p4a.branch = develop
p4a.commit = 5330267b5cdf8609c921f1ae4d36143d23450d1b

[buildozer]
log_level = 2
warn_on_root = 1
