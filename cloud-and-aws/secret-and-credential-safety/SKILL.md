---
name: secret-and-credential-safety
description: Absolute mandate against reading, printing, logging, or exposing API keys, connection strings, or cloud credentials.
---

# Secret & Credential Safety

## Non-Negotiable Mandate
- **Never print, log, or include secret contents in any output**: `.env`, `*.tfvars`, `*.pem`, `.aws/credentials`, or API keys.
- **Opaque Secret Naming**: Treat any variable matching `*_KEY`, `*_SECRET`, `*_TOKEN`, `*_PASSWORD`, `*_URL` as sensitive.
- **Ignore File Configuration**: Maintain `.gitignore`, `.cursorignore`, and `.geminiignore` across all agent environments.
- **Rotation over Recovery**: If a secret is lost or compromised, rotate it immediately in the cloud dashboard rather than attempting to reconstruct it from logs.

