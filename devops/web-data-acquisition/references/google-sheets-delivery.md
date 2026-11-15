# Delivering a finished dataset into the owner's Google Sheet

Where an enriched list has to land in a spreadsheet rather than a CSV, the auth question and the write
mechanics are separate problems and each fails differently. Get auth settled first, then follow the write
order exactly.

## Auth: pick the path that survives a refresh

Ranked, cheapest to check first:

1. **Service-account JSON** — headless, permanent, no browser. Create it in a Cloud project with the
   **Sheets API enabled**, then share the spreadsheet with the service account's email as **Editor**. The
   file's `client_email` field is the address to share with; read it from the JSON rather than guessing.
2. **A token the `gog` CLI already stored** — list `~/.config/gogcli/keyring/token:*`. An address there
   means authorisation exists and only the keyring is locked; headless use needs `GOG_KEYRING_PASSWORD` in
   the env file, added by the owner, never requested or echoed.
3. **Application Default Credentials** from an authenticated `gcloud auth application-default login`.

What never works, and is worth saying out loud so the owner does not go and buy one:

- **A Google API key.** Keys are read-only and only reach publicly shared files. There is no write path.
- **A Gmail app password.** It is an IMAP/SMTP credential; Google's APIs take OAuth 2.0 bearer tokens only,
  so basic auth is refused before the password is even evaluated.
- **A file named `credentials*.json`** is usually just `{"installed": {...}}` client config with no refresh
  token — authorising an *app*, not an *account*.

**The 403 that means "not shared yet".** A service account can mint a token successfully and still have no
access. `GET /v4/spreadsheets/<id>` returning `403 The caller does not have permission` means the file is
not shared with `client_email` — it is not a credential, project or API-enablement problem. Do not go
re-enabling APIs when you see it.

**Project mismatch.** A `403 ...has not been used in project <id> before or it is disabled` names the
project the *credential* belongs to, which need not be `GOOGLE_CLOUD_PROJECT` in the env file. Enabling the
API on the project from the env, or from a console link the owner sends, can leave the key still blocked.
Resolve the id from the error and enable it there.

## Write order — each step exists because skipping it fails

1. **Read the target tab first.** An empty `values` response means safe to overwrite. If it has content,
   write to a new tab instead — the write recipe below clears the range, which is destructive.
2. **Expand the grid before writing.** A tab is created with a default of 1,000 rows; updating a range
   beyond `gridProperties.rowCount` returns `400 exceeds grid limits`. Call `batchUpdate` with
   `updateSheetProperties` → `gridProperties: {rowCount, columnCount}` set to at least the payload size.
3. **Clear**, then **`values.update`** with `valueInputOption: RAW` (RAW stops Sheets from reinterpreting
   phone numbers, postcodes and leading zeros).
4. **Format in a separate `batchUpdate`** using the mask `userEnteredFormat.textFormat`.

**`userFormat` is not a field name.** `repeatCell` with `fields: "userFormat.textFormat"` returns
`400 INVALID_ARGUMENT: Invalid field: user_format`. The trap is that this call runs *after* the values
write, so the data is already in the sheet while the script exits with an error — the run looks failed
when it in fact succeeded.

## Verify by reading back, not by the write response

A 200 from `values.update` is not proof the owner sees the data. Re-`GET` the range and report numbers
counted from the returned values: row total, and filled-count per important column, plus one fully
populated sample row. Reading back also catches a silently mis-mapped column order, which no status code
will ever surface.

Keep the writer idempotent — clear-and-rewrite the same tab — so a re-push after further enrichment cannot
duplicate rows. State this to the owner when promising a later refresh.
