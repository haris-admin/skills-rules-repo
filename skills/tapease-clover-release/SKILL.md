---
name: tapease-clover-release
description: >-
  Build, check, sign and record the Tap-Ease Driver Terminal Android app (com.tapease.driverterminal) for the Clover App Market. Use when asked to make a release APK, sign it, resubmit or withdraw a version, prepare Clover release notes, or confirm Sentry and production settings in a build. Covers the versionCode rule, the Sentry and host checks, V1-only signing without printing passwords, and tagging.
---

# Release the Tap-Ease terminal app to the Clover App Market

Repo `tapease-termianl-pos-app`, app under `tapease_pos_app/`. Full build and upload steps live in `docs/clover-release-handoff.md`; the Clover-facing note is `tapease-pos-release.md`.

## Rules that cannot be broken

- **Every upload needs a higher versionCode than the last upload**, even a withdrawn and resubmitted version (Clover: "You must increment your APK's versionCode every time you upload"). Change `versionCode` in `app/build.gradle.kts` and the test `NativeLibPackagingTest.T59_03` together, test first.
- The same production keystore signs every version. V1 (JAR) signing only; V2, V3, V4 off. Never use the debug or staging keystore for production.
- Never print a password or the Sentry DSN key. The production passwords are in `keystore-credentials-production.local.txt` (gitignored).

## Procedure

1. Full unit suite green (`./gradlew :app:testDeviceDebugUnitTest`), read the result XML (the background "exit 0" is only the launcher).
2. Build from a clean, named commit: `./gradlew assembleCloverUploadRelease` (no `-PstagingBuild=true`). Do NOT override `SENTRY_DSN` with an empty value; it comes from `local.properties`.
3. `zipalign -p -f 4` the unsigned APK, then check it: `aapt dump badging` (versionCode, versionName), the dex strings: only `https://api-pos.tapease.com.au`, exactly one Sentry DSN (print the host only), the environment string `production`, `unzip -lv ... | grep .so` all `Defl:N`, and the bundled assets and licences present.
4. Sign with a short script that reads the store and key passwords from the credentials file into environment variables (`--ks-pass env:KSPW --key-pass env:KEYPW`), prints nothing secret, and finishes with `apksigner verify` (v1 true, v2 to v4 false), `zipalign -c -p 4`, the certificate SHA-256 and the file SHA-256. Run it only when the owner has asked; if the classifier blocks it, hand over `! ~/sign-prod.sh`. Delete the script afterwards.
5. Record the file name, SHA-256, certificate SHA-256 and source tag in the release notes and the Clover note. Tag the source commit with a new tag (never move one).
6. Keep the previous APK for rollback. Clover also suggests submitting a copy of the previous version with a higher code if a rollback is needed.

## Clover-facing note

Short and plain: one line per change, simple English, how to try it in five steps, build facts, third-party components (fonts, data) with their licences. Keep engineering detail in the release notes.

## Production checks before upload

Backend `/health`: version, `environment: production`, `sentry.enabled: true`; read-only error counts since the last restart (see the POS backend deploy skill). Do not upload a staging build: the staging build calls the staging host.

## Installing on the Flex 4 test device

The Dev Kit runs the debuggable `device` build: `./gradlew :app:installDeviceDebug` updates it in place and keeps the pairing. A release-signed APK has a different certificate and needs an uninstall (which wipes the pairing). The Start Shift screen only shows when no shift is open; do not end the owner's shift to take a screenshot.
