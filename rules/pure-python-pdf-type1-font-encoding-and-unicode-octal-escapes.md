# Pure-Python PDF Type 1 Font Encoding and Unicode Octal Escapes

Zero-dependency PDF 1.4 generators that render text with standard Type 1 fonts (`/BaseFont /Helvetica`) must declare `/Encoding /WinAnsiEncoding` and translate Unicode glyphs to Windows-1252 octal escapes in PDF string literals.

**Scope:** Any backend or service generating raw PDF documents without external libraries (ReportLab, WeasyPrint, PyMuPDF, etc.).

---

## Problem

When writing raw PDF text streams `( ... ) Tj`, emitting multi-byte UTF-8 string data directly causes character corruption in standard PDF readers:
- The bullet point `•` (`\u2022`, UTF-8 byte sequence `0xE2 0x80 0xA2`) has its trailing byte `0xA2` interpreted in standard Adobe font encoding as the cent sign (`¢`).
- A masked card number like `Mastercard •••• 1234` renders as `Mastercard ¢¢¢¢ 1234`.
- Middle dot separators `·` (`\u00b7`, UTF-8 `\xC2 0xB7`) render as `´•`.
- Smart quotes (`“`, `”`, `‘`, `’`) and dashes (`–`, `—`) render as garbled multi-byte glyph combinations.

## Root Cause

Standard Type 1 fonts in PDF 1.4 do not parse multi-byte UTF-8. Without an explicit `/Encoding` entry in the font dictionary, PDF viewers default to `StandardEncoding`, where byte values above 127 map to Adobe standard symbols rather than Latin/Unicode codepoints.

## Required Solution

1. **Explicitly declare `/Encoding /WinAnsiEncoding` on all Type 1 font dictionaries:**
   ```pdf
   << /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>
   << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>
   ```

2. **Implement an escaping helper that maps Unicode characters to WinAnsi octal escape sequences in PDF string literals:**
   ```python
   def _escape_pdf_text(text: str) -> str:
       """Escapes PDF delimiters and maps Unicode characters to WinAnsi octal escapes."""
       escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
       replacements = {
           "\u2022": "\\225",  # bullet • (0x95 = octal 225)
           "\u00b7": "\\267",  # middle dot · (0xB7 = octal 267)
           "\u2013": "\\226",  # en-dash – (0x96 = octal 226)
           "\u2014": "\\227",  # em-dash — (0x97 = octal 227)
           "\u2018": "\\221",  # left single quote ‘ (0x91 = octal 221)
           "\u2019": "\\222",  # right single quote ’ (0x92 = octal 222)
           "\u201c": "\\223",  # left double quote “ (0x93 = octal 223)
           "\u201d": "\\224",  # right double quote ” (0x94 = octal 224)
           "\u20ac": "\\200",  # euro € (0x80 = octal 200)
       }
       for char, octal_seq in replacements.items():
           escaped = escaped.replace(char, octal_seq)
       return escaped
   ```

3. **Verify with visual crops:**
   Render the generated PDF with `pdftoppm -png -r 150 <file.pdf> <out>` and inspect the cropped visual text output before marking tasks complete.

## Why this exists

**8 Nov 2026 (Tapease POS Driver Terminal v1.1.12):** Digital PDF receipts downloaded via on-screen QR codes displayed `Mastercard ¢¢¢¢ 5678` instead of bullets because Helvetica lacked `/WinAnsiEncoding` and raw UTF-8 bytes were emitted into the PDF content stream.

