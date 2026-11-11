# Release tags are additive: one new tag per build, never moved or force-pushed (all agents, all repos)

Tag the exact source of every build that leaves the building. If a build is replaced, give the new build a new tag and leave the old one in place.

## Why this exists
**11 Nov 2026, Tap-Ease POS 1.1.12:** the submitted build was tagged `v1.1.12`. When it was withdrawn and rebuilt, moving the tag meant a force-push, which the auto-mode classifier blocked as destructive (and the whole compound command, including the commit, did not run). Creating `v1.1.12-resubmit` and later `v1.1.12-code19` was safe, and the history of which build was which stayed readable.

## Rules
1. Tag each submitted or deployed build at the commit it was built from, with a message that names the artifact (versionCode, checksum if known).
2. Never delete, move or force-push a published tag. Add a new one (`v1.1.12-resubmit`, `v1.1.12-code19`).
3. Record in the release notes which tag is which build and which were withdrawn or rejected.
4. Do not chain a force operation into a longer command; a blocked destructive step blocks everything in the same call. If the classifier blocks one, take the additive route instead of working around it.
