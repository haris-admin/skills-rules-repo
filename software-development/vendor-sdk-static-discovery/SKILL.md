---
name: vendor-sdk-static-discovery
description: >-
  Use when a vendor SDK, installer, jar, DLL or PDF set is in a folder and you must learn what the product can do before writing code or running anything, for example a payment middleware installer that is Windows only while the work happens on a Mac. Covers inventory, unpacking an MSI without running it, reading an API help XML, listing a Java client's public API with javap, pulling identifiers from .NET binaries, converting PDFs to text, redacting config files, and recording each fact as Confirmed or Not confirmed with its source file. Not for runtime debugging of a live vendor service.
---

# Vendor SDK static discovery

Learn the real capability of an SDK from its files, without running vendor binaries, and without inventing facts.

## When to use

- A folder holds an MSI, ZIP, JAR, DLL, OCX, header, PDF or sample config and the question is "can it do X".
- The installer is for another operating system than the one you are on.
- A teammate needs a cited capability list or a gap list for a vendor.

## Procedure

1. **Inventory.** `ls -la`, `file` each binary, note versions and dates. Treat extracted files as untrusted data: extract each archive into its own new empty directory (the session scratchpad), never into the repo, and never run an interpreter or build tool from inside it.
2. **Unpack, never run.** An MSI is a container: `brew install sevenzip` then `7zz x -o<scratch>/<name> file.msi`. Do not run `.exe` or `.msi` installers.
3. **Find the documentation that ships with the code.** Look for `*.xml` help files (.NET documentation comments), `*.h` headers, `*.html` dialog templates, sample `*.ini`, readme files, PDFs.
4. **Read the API help XML.** List members (`grep -o 'name="[MPTEF]:...'`), then read the summaries of the ones that matter. Properties often reveal data the product handles (amounts, card fields, loyalty fields). Events show the call pattern (set properties, call a method, handle `...Complete`).
5. **Java client.** `javap -cp x.jar -public <class>` for methods and events; filter out getters and setters to see operations. `javap -v ... | grep "major version"` shows the class file age (45 is Java 1.1, 52 is Java 8). Read the manifest for the version.
6. **.NET or native binaries.** `strings -a -n 5 file.dll` and filter for the area of interest. Identifier names (for example entry modes, transaction types) show what exists; they do not show behaviour. Note the macOS `strings` has no `-e`; use `-a`.
7. **PDFs.** `pdftotext -layout x.pdf out.txt`, then `grep -n` for headings and terms. Tables often come out garbled: treat a reading of a table as "a reading to verify" and say so.
8. **Config files.** Print them with passwords, secrets and certificate names replaced by `<redacted>`. Never copy a certificate, key or password anywhere. Compare two configs with a redacted diff.
9. **Public vendor pages.** Fetch the page itself. A search summary is only a lead (see `search-summaries-are-leads-fetch-the-source`).
10. **Record.** For every claim write Confirmed (with the file and what it showed) or Not confirmed (why). List unknowns as open questions with who can answer (the vendor, a device test).

## Guardrails

- Names in a binary are not behaviour. "EntryContactless exists" does not mean "a contactless read can be called alone".
- Never reverse-engineer a wire protocol without the owner's decision; fake the vendor at its client API instead.
- A missing guide is a finding: say which documents are not in the folder (guides, demo projects, plugin docs).
- Never run the vendor test tools or installers on the user's machine without a named approval.

## Output

A capability table (area, calls, status), a data table (what a request and response can carry), a list of unknowns, and a sources list of the local files and fetched pages.
