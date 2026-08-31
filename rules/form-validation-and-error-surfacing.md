# Form Validation & Error Surfacing Standards

**Canonical rule.** Applies to all frontend and backend forms, user profile updates, authentication endpoints, and API proxies.

## 1. International Identity & Name Validation

- **Never restrict personal names to ASCII `[A-Za-z0-9 ]` or English-only regexes.**
- Names across Australia and worldwide contain apostrophes (`O'Brien`, `D'Angelo`, `D’Angelo`), hyphens (`Anne-Marie`, `Smith-Jones`), periods (`St. John`, `J. R.`), spaces, and international Unicode diacritics / non-Latin characters (`José`, `Nguyễn`, `François`, `Müller`, `Björn`, `Łukasz`, `李`, `احمد`).
- **Allowed Character Sets**:
  - Frontend and Backend schemas must support Unicode letters (`\p{L}`), combining marks (`\p{M}`), spaces, apostrophes (`'` and `’`), hyphens (`-`), and periods (`.`).
  - Max length: Standard 100 characters per field unless explicitly specified.
- **XSS & Injection Defense**:
  - Explicitly reject or sanitize `< >`, `<script>` tags, `javascript:` URIs, and event handlers (`on*=\w+`), without rejecting legitimate punctuation (apostrophes, hyphens, periods).
- **Matching Contracts**:
  - Frontend client validation rules MUST match or be strictly aligned with backend Pydantic/FastAPI schemas.
  - Never allow a field on the client that the backend schema rejects with a 422, and never prematurely reject valid inputs on the client that the backend supports.

## 2. Error Surfacing & Observability (Never Swallow 422s)

- **Field-Specific Errors Must Be Preserved and Displayed**:
  - When an API call returns HTTP 422 (Unprocessable Content) or validation errors (e.g. FastAPI `detail[]` arrays formatted into `error.message` or `response.msg`), form submission handlers (`catch` blocks) MUST display the specific field message to the user.
  - **Forbidden**: Discarding `error.message` in favor of a hardcoded generic string like `"Registration failed. Please try again."` or `"An error occurred."`
  - **Fallback Pattern**:
    ```javascript
    const errorMessage = error?.message && error.message !== "An error occurred" && error.message !== "Request failed"
      ? error.message
      : "Operation failed. Please try again.";
    setSubmitError(errorMessage);
    ```
- **Error Transparency**:
  - If a user enters invalid input, the UI must highlight or display which field failed and the reason why, enabling immediate self-service correction without requiring customer support.
