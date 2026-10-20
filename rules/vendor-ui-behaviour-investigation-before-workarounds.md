# Vendor ui behaviour investigation before workarounds

When a third-party UI screen cannot be controlled through documented settings, read the vendor app's own logs and code on the device before concluding or building a workaround.

**Scope:** any agent integrating with a vendor app that draws its own screens (payment terminals, kiosks, SDK activities).

## Why this exists

Added 19 Oct 2026 (TapEase POS). Clover's "All Done! Thank you for your purchase" screen stayed up until touched. Several request settings were tried over days and did nothing. Reading the device log and the vendor APK's bytecode (`dexdump`) showed in one pass that the extra we set is only read by the tip and card-vault flows, and that the screen is Clover's customer-mode handoff.

## Core Directives

1. **Log first.** Capture the device log around the screen (activity starts, state changes) and name the exact vendor activity and state.
2. **Then read the vendor code read-only.** Pull the vendor APK into a scratch folder, dump it, and find where each setting you send is actually read. Do not install, patch or repackage it.
3. **Prove a setting does something** before relying on it. A constant that exists is not proof; find its readers.
4. **Label the result as evidence, not proof.** Vendor code is obfuscated; say what was and was not found.
5. **Record it and ask the vendor.** Put the finding in `docs/` and the question in the vendor email. Prefer a supported setting over an app-side workaround that races the vendor's result.

## Verification & Guardrails

- Never modify system settings on the device to test a theory; give the user the setting to try.

## Addendum, 20 Oct 2026 (TapEase POS, same Clover screen)

6. **Compare against the last known-good request before blaming your own flags.** When told "it did not show before", diff what the app sent in that release (`git show <commit>:<path>`) against now. Here the 29 Sep release sent a subset of today's request, so no flag had been lost.
7. **Record the vendor app version with every device test.** Clover's payment app moved from 758 to 935 between tests (`dumpsys package <pkg>`: `versionName`, `lastUpdateTime`). A vendor update can change behaviour with no change of ours.
8. **A request that cannot start is not a failed experiment.** A spike through a different launch route (PayIntent) died with "no order ID" in 200 ms and proved nothing about the setting. Re-test through the production route and check the log shows the payment actually ran.
9. **`apkanalyzer dex code --class <name> <apk>` prints readable smali** without a decompiler. Use it to find the decision (`if isCustomerMode()`, who calls `CustomerMode.disable`) instead of guessing extras from string tables.
10. **One experiment at a time, with one on-device payment each**, and log the result in the investigation doc: what was sent, what the log said, whether it was conclusive. Revert the experiment code afterwards and reinstall the committed build.

## Addendum 2, 20 Oct 2026 afternoon (TapEase POS, the same screen solved)

The 19 Oct conclusion "cannot be suppressed by request settings" was wrong. The screen was reached **because of one of our own settings** (`SkipReceiptSelection()`), and enabling a single receipt option (No receipt) plus a vendor timeout extra removed it on the device.

11. **Trace backwards from the screen's call site and read every branch condition on the way, not only the branch you are in.** Ask of each condition: which value would skip this, and does anything we send decide it? Here `isReceiptSelectionScreenDisabled()` was true only because we asked for it; the other branch finished with no dialog.
12. **Do not call a vendor screen unremovable until every setting you send that feeds the path has been flipped once.** A setting added to remove a different screen can be the one that routes into this one.
13. **Find the vendor's own request handler and list every extra it reads** (`apkanalyzer dex code --class <Handler>` then grep `const-string .*intent.extra`). This found `EXTRA_RECEIPT_SELECTION_TIMEOUT_THRESHOLD`, which no doc mentioned.
14. **Keep a working experiment as a named local branch when the user asks**, one commit per proven value, instead of reverting it. Nothing on it reaches the main branch without the normal requirement and failing test.
15. **A unit test that counts builder options cannot tell enabled from disabled.** Assert each option's own flag, or the test passes for both the old and the new request.
