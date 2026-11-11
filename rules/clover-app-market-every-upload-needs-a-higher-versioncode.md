# Every upload to the Clover App Market needs a higher versionCode (Android release work, all agents)

Clover refuses an APK whose versionCode is not higher than the last one uploaded, even when the earlier upload was withdrawn and the same version is being resubmitted. Bump the versionCode before every upload.

## Why this exists
**11 Nov 2026, Tap-Ease terminal app 1.1.12:** Haris withdrew a submitted 1.1.12 (versionCode 18) and asked for it to be resubmitted "at version 18" to include one more change. Clover answered "Oops! Invalid File! You must increment your APK's versionCode every time you upload." Two builds were signed for nothing. The assistant had mentioned the rule only in passing and then accepted "version 18".

## Rules
1. Before building any APK for upload, ask what the last uploaded versionCode was, and set the new one higher. The version name may stay the same; only the code must rise.
2. When the owner asks to resubmit "at the same version", say plainly that the versionCode must still go up, and offer the choice: same name with a higher code (recommended), or a new version name (which also moves any backend that is released in tandem).
3. Change the versionCode and the test that pins it together, test first (the test must fail against the old number).
4. Record every uploaded build (versionCode, SHA-256, source tag), including builds Clover rejected, so the next bump is obvious.
5. Side-loading is the only way around the rule and is for testing, never for a submission.
