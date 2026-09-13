---
name: secret-and-credential-safety
description: Absolute mandate against reading, printing, logging, or exposing API keys, connection strings, or cloud credentials. Use whenever a task could read, print, log, or commit a secret-shaped value (.env, .tfvars, .pem, .aws/credentials, *_KEY/*_SECRET/*_TOKEN), or when setting up ignore files across agent tools, or recovering from a suspected credential leak.
---

# Secret & Credential Safety

## Non-Negotiable Mandate
- **Never print, log, or include secret contents in any output**: `.env`, `*.tfvars`, `*.pem`, `.aws/credentials`, or API keys.
- **Opaque Secret Naming**: Treat any variable matching `*_KEY`, `*_SECRET`, `*_TOKEN`, `*_PASSWORD`, `*_URL` as sensitive.
- **Ignore File Configuration**: Maintain `.gitignore`, `.cursorignore`, and `.geminiignore` across all agent environments.
- **Rotation over Recovery**: If a secret is lost or compromised, rotate it immediately in the cloud dashboard rather than attempting to reconstruct it from logs.

