---
name: android-terminal-readonly-probe
description: >-
  Use when an Android payment terminal or other locked-down Android device is connected by USB and you need to know what it is and what it runs before building or installing anything. Runs only read-only adb queries (model, Android version, ABI, build type, foreground app, home launcher, installed third-party and vendor packages, camera and hardware features) and explains how to read the results. Covers the macOS case where system_profiler shows nothing but adb works, and the point where a named approval is needed before any install. Not for installing, signing or debugging apps.
---

# Android terminal read-only probe

Find out what a connected device is, safely, before the first build.

## When to use

- The user says a terminal is connected and asks you to check it.
- You need minSdk, ABI and vendor package facts for a new app.
- You must decide whether an app can be installed unsigned.
- Do NOT use to install, uninstall, change settings, or run anything that writes.

## Procedure (all read-only)

1. **Is it visible?** `adb devices -l`. The state must be `device` (not `unauthorized` or `offline`). On macOS `system_profiler SPUSBDataType` can print nothing while adb still works, so trust adb. If adb is not on PATH, look under the Android SDK (`$ANDROID_HOME/platform-tools`).
2. **Identity and build.** `adb shell getprop` for `ro.product.manufacturer`, `ro.product.model`, `ro.build.version.release`, `ro.build.version.sdk`, `ro.product.cpu.abi`, `ro.build.type`, `ro.debuggable`, `ro.secure`, `ro.build.fingerprint`.
3. **What is on screen and who is home.** `adb shell dumpsys window | grep -E "mCurrentFocus|mFocusedApp"` and `adb shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME`.
4. **What is installed.** `adb shell pm list packages -3` (third party, which on a terminal includes the vendor's own payment apps) and `adb shell pm list packages | grep -i -E "<vendor>|usdk|launcher|kiosk"`.
5. **Hardware.** `adb shell pm list features | grep -i -E "camera|nfc|bluetooth"`.
6. **Write down** the model, Android release and API level, ABI, build type, the foreground app, the vendor service packages (for example an SDK service and an ECR or POS service) and whether any custom app exists.

## Reading the results

- `ro.build.type=user`, `release-keys`, `ro.debuggable=0`: a locked production build. adb is allowed (developer mode is on) but you cannot assume root, system app installs or permission grants.
- A 32-bit ABI (`armeabi-v7a`) means the app and any native library must include that ABI.
- The API level is the app's minSdk.
- A vendor launcher in the foreground is the payment shell. It is not a sign the device is broken.
- Whether an unsigned app can use vendor SDK modules (scanner, contactless reader) depends on the vendor's signature levels. That is a finding to confirm, not a guess.

## Guardrails

- Stop at read-only. `adb install`, `adb push`, `adb shell settings put`, `pm grant`, `am start` of vendor apps, reboots and factory actions each need a named approval from the user for that action.
- The device serial number is an identifier: keep it out of shared pages, commit messages and external services.
- If adb needs a vendor id added to `adb_usb.ini`, ask before creating the file.
- Close other vendor tools that hold adb (a toolkit may take adb over while running).

## Output

A short table: model, Android and API level, ABI, build type, foreground app, vendor packages, camera features, custom apps, and a "Not confirmed" list (variant, signing level, vendor permissions).
