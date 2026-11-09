# Customer Receipt vs Driver Settlement Support Channel Segregation

Passenger/customer receipts and driver settlement reports serve distinct audiences and must expose strictly segregated support channels.

**Scope:** Receipt generation, shift settlement reports, terminal UI, and public document streaming.

---

## Directives

1. **Passenger Receipts:**
   - Must only display public customer support channels (e.g. `Support: help@tapease.com.au`).
   - Must **never** expose internal driver hotline numbers (`1300 ...`) or operational/dispatch mobile numbers (`04...`).
   - Keeps the passenger support queue clean and prevents general transport inquiries from flooding dedicated driver phone lines.

2. **Driver Shift Settlement Reports:**
   - Must provide the direct driver assistance line (`1300 990909`) and support email (`help@tapease.com.au`) for dispute and settlement queries.
   - Must **never** display mobile numbers reserved strictly for programmatic SMS notifications.

3. **Mobile Numbers:**
   - Mobile numbers are reserved exclusively for machine-to-human SMS options (e.g., C64 scannable diagnostic QR codes for terminal faults).
   - Never print or render mobile numbers as general support contact lines on printable or downloadable documents.

## Why this exists

**8 Nov 2026 (Tapease POS Driver Terminal v1.1.12):** Initial draft footers grouped the 1300 number, mobile SMS number, and email together on both passenger receipts and driver shift reports. Haris clarified that passenger receipts must be email-only, driver settlement reports should include the 1300 number, and mobile numbers must remain reserved exclusively for automated SMS dispatch.

