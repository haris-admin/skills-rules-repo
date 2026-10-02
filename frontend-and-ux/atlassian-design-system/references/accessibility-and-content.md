# ADS Accessibility and Content

Reference for `atlassian-design-system`. Sources:
<https://atlassian.design/foundations/accessibility> and <https://atlassian.design/foundations/content>.

## Accessibility

> "When apps are accessible, the experience is better for everyone."

ADS components ship built-in keyboard support and sensible ARIA — **but that is not an accessible
app**. You must still review patterns, content and interactions end-to-end. This is the sentence to
quote when someone argues that "we used the component library, so we're accessible".

### The eight principles

1. **Build consistent experiences.** Familiar, identifiable, works regardless of device, screen size,
   platform, or assistive technology. Build on design-system components; use the same component,
   pattern and interaction for the same experience everywhere (less cognitive load).
2. **Keep experiences and language simple.** Avoid complex processes; reuse patterns; concise plain
   language; **write to a reading level of ages 12–14**.
3. **Be inclusive.** Inclusive language; never assume ability; **avoid jargon, metaphors and
   non-literal phrases** (see inclusive-writing guidance).
4. **Give people control.** Enable reflow at all screen sizes; allow adjustment of scale, contrast and
   colours; respect personal **reduced-motion** settings; inform people about high-impact changes
   *before* making them.
5. **Provide text alternatives.** Visible and accessible labels; clear, concise labels and alt text;
   include or link a transcript for video.
6. **Ensure colour is accessible.** Never rely on colour alone; **4.5:1 for regular text, 3:1 for
   large text and graphics**.
7. **Use semantic HTML.** `header`, `nav`, `footer` — real elements convey meaning to browsers and
   assistive tech; `div`/`span` do not.
8. **Test apps broadly.** Test with different tooling (e.g. Accessibility Insights) **and with people
   with disabilities**, across levels of technical experience.

### Disability classes — design for all four, never one in isolation

The framing is deliberate: **everyone experiences disability at some point** — permanently,
temporarily, or situationally.

| Class | Requirements | Permanent / Temporary / Situational |
|---|---|---|
| **Visual** | Alt text + semantic HTML; not colour alone; accessible contrast | Blind / migraine / lost glasses |
| **Auditory** | Closed captions and transcripts for video; transcripts for audio | Deaf / ear infection / on public transport |
| **Limited mobility** | Keyboard navigation; large selectable targets; correct semantic HTML | Cerebral palsy / broken wrist / holding a baby |
| **Cognitive** | Plain clear wording; break up text with headings, bullets, short paragraphs; easy to navigate | Dyslexia / anxiety / busy office |

> The situational column is the persuasive one with stakeholders: "on public transport" and "busy
> office" are ordinary conditions, not edge cases.

### Benefits
Accessibility considered throughout design and development produces apps that **benefit everyone**,
reach more people, **comply with legislation**, and stay innovative.

## Content

Content is at the heart of quality interfaces. Five guidelines:

| Guideline | Scope |
|---|---|
| **Inclusive language** | Inclusive content and experiences; includes the "avoid metaphors and idioms" rule |
| **Style, grammar, punctuation** | Writing conventions that keep UI clear, consistent and **localizable** |
| **Voice and tone** | UI and app content that aligns with Atlassian's voice and tone |
| **Date and time** | Communicate date/time clearly and consistently **wherever customers are located** |
| **Designing messages** | How to write and format success and error messages and other alerts |

### Rules worth enforcing in review

- **Sentence case**, plain language, and a **12–14 reading age**.
- **No idioms, metaphors, or non-literal phrasing** — they break translation and exclude readers.
- **Dates and times**: never assume the reader's locale or timezone. (Directly relevant to us: we
  operate in AEST/UTC and mix both — a UI that shows a bare `30/09/2027` is ambiguous to a US reader
  and wrong for anyone outside AU.)
- **Messages**: success and error text is designed, not typed on the way out the door. An error should
  say what happened and what to do next.
- **Localizable by construction** — no string concatenation, no hardcoded punctuation assumptions.

## Key pages
- Accessibility: <https://atlassian.design/foundations/accessibility>
- Inclusive writing: <https://atlassian.design/foundations/content/inclusive-writing>
- Style, grammar, punctuation: <https://atlassian.design/foundations/content/language-and-grammar>
- Voice and tone: <https://atlassian.design/foundations/content/voice-tone>
- Date and time: <https://atlassian.design/foundations/content/date-time>
- Designing messages: <https://atlassian.design/foundations/content/designing-messages>
