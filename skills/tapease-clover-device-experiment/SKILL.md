---
name: tapease-clover-device-experiment
description: >
  How to run one on-device experiment against Clover's payment app on the Tap-Ease
  Flex 4 terminal: read Clover's code read-only, build an experiment APK from a
  throwaway git worktree, have Haris sign it (V1, release key) through a Terminal
  script, install it, watch logcat for the payment, and record the result. Use when
  a Clover screen or flow must be changed through the payment request ("can we
  suppress that screen", "try this flag on the device", "why does Clover show X"),
  or when signing a staging APK fails through `!`. Not for releases (see
  tapease-backend-deploy and doc/clover-release-handover); rules that govern this
  are vendor-ui-behaviour-investigation-before-workarounds and
  handoff-commands-as-short-script-files.
---

# Tap-Ease Clover device experiment

Repo: `mapp` (`tapease_pos_app/`). Device: Flex 4 over USB (`adb devices -l`, model C406).
The payment request is built in `RealCloverPaymentGateway.configureBuilder` and
`applyNoExtraScreens`.

## 1. Read Clover first (read-only)

```bash
S=<scratchpad>/pay; mkdir -p $S
adb shell pm path com.clover.payment.builder.pay          # base.apk path
adb pull <path> $S/pay.apk
adb shell dumpsys package com.clover.payment.builder.pay | grep -m2 -E "versionName|lastUpdateTime"   # record this
apkanalyzer dex packages $S/pay.apk | grep -E "^C .*PayActivity"   # find the real class name
apkanalyzer dex code --class com.clover.payment.builder.pay.activities.PayActivity $S/pay.apk > $S/PayActivity.smali
```

- Find the log line the device printed, then read the branch conditions above it. Ask which of
  OUR settings decides each one (20 Oct 2026: `SkipReceiptSelection()` was what led to All Done).
- List every extra the request handler reads:
  `apkanalyzer dex code --class com.clover.payment.builder.pay.handler.PaymentRequestHandler\$1 ... | grep "const-string .*intent.extra"`.
- SDK side: `javap -p -c` on classes from the Gradle cache jar
  `~/.gradle/caches/*/transforms/*/transformed/clover-android-sdk-334-runtime.jar`.
- Never install, patch or repackage Clover's app.

## 2. Build the experiment in a throwaway worktree

```bash
W=<scratchpad>/wt
git worktree add --detach $W HEAD
cp tapease_pos_app/local.properties $W/tapease_pos_app/
# one change only, then:
cd $W/tapease_pos_app && ./gradlew assembleCloverUploadRelease -PstagingBuild=true -q
# output: app/build/outputs/apk/cloverUpload/release/app-cloverUpload-release-unsigned.apk
```

The release build uploads its debug files to Sentry by itself; say so in the report.

## 3. Signing: Haris runs it, through Terminal

The agent never reads the keystore passwords (`keystore-credentials*.local.txt` is off limits).
`! <script>` has no keyboard input, so a password prompt fails ("standard input closed").
Write `~/<short>.sh` that:

- `read -r -s` the keystore and key passwords, strips whitespace and non-printing characters,
  exports them and calls `apksigner sign --ks tapease_pos_app/tapease-driverterminal-release.keystore
  --ks-key-alias tapeasedriverterminal --ks-pass env:VAR --key-pass env:VAR2
  --v1-signing-enabled true --v2-signing-enabled false --v3-signing-enabled false
  --v4-signing-enabled false --v1-signer-name CERT --min-sdk-version 21 --out ~/tapease-staging-<ver>-<tag>.apk <unsigned>`
  (apksigner: `/opt/homebrew/share/android-commandlinetools/build-tools/35.0.0/apksigner`),
- then `adb install -r`, `adb logcat -c`, starts `com.tapease.driverterminal/.MainActivity`,
- `tee`s non-secret output to `~/<short>.log`, traps errors with the line number, and ends with
  `read -r -p "Press Return to close."`.

Run `bash -n`, then give Haris only `! open -a Terminal ~/<short>.sh`. Opening it twice gives two
windows at one prompt. Watch the log with a background `until grep -q -E "Installed|FAILED" ~/<short>.log`.

## 4. One payment, read the log

Wait in the background for the flow to end, then read only the decisive lines:

```bash
until adb logcat -d | grep -q -E "PayActivity: performFinish|Return to Merchant"; do sleep 3; done
adb logcat -d | grep -v WindowManager | grep -E "CardBrandPlayer|PayActivity: (goToCurrentState|startReceipt|performFinish)|RECEIPT_SCREEN_TIME|Return to Merchant|Displayed com.clover"
```

Key Clover states: `COMPLETE, customerMode: true` after "Return to Merchant" = the All Done screen.
`performFinish` with no `COMPLETE` = Clover returned without it.

## 5. Record and finish

- Add the experiment to the investigation doc in `docs/`: what was sent, Clover app version, log
  times, Haris's words, conclusive or not.
- Revert the experiment and reinstall the committed staging APK, unless Haris asks to keep it.
  If he asks to check it in as an option, commit it on a named local branch
  (`spike/<topic>`), one commit per proven value, never on `dev`, never pushed.
- The production change still needs its OpenSpec requirement and failing tests first.
- Remove the worktree when the branch is no longer needed (`git worktree remove`).
