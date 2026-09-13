# HTML / CSS / JS Standards

Technical baseline for any standalone HTML artifact this skill produces.

## Use modern CSS well

- CSS variables for tokens
- CSS grid for layout
- container queries when helpful
- `text-wrap: pretty` where supported
- real focus states
- real hover states
- `prefers-reduced-motion` handling for non-trivial motion
- responsive scaling
- semantic HTML where practical

## Avoid

- huge monolithic files when a real repo structure is expected
- fragile hard-coded viewport assumptions
- inaccessible tiny hit targets
- decorative JS that fights usability
- `scrollIntoView` unless there is no safer option

## Sizing minimums

- Mobile hit targets should be at least 44px.
- For print documents, text should be at least 12pt.
- For 1920×1080 slide decks, text should generally be 24px or larger.
