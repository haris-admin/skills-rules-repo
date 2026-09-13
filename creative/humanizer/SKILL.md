---
name: humanizer
description: "Identifies and removes signs of AI-generated writing (34 documented patterns: significance inflation, copula avoidance, em-dash overuse, filler phrases, and more) and adds natural voice/personality back into the text. Use when asked to humanize, de-AI, de-slop, or un-ChatGPT a piece of text, to rewrite a draft so it doesn't sound machine-generated, to match a writer's own voice from a sample, or to review text for AI tells before publishing — including the assistant's own user-facing prose (release notes, PR descriptions, docs, summaries)."
version: 2.5.1
author: Siqi Chen (@blader, https://github.com/blader/humanizer), ported by Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [writing, editing, humanize, anti-ai-slop, voice, prose, text]
    category: creative
    homepage: https://github.com/blader/humanizer
    related_skills: [songwriting-and-ai-music]
---

# Humanizer: Remove AI Writing Patterns

Identify and remove signs of AI-generated text to make writing sound natural and human. Based on Wikipedia's "Signs of AI writing" guide (maintained by WikiProject AI Cleanup), derived from observations of thousands of AI-generated text instances.

**Key insight:** LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely completion, which is how the telltale patterns below get baked in.

## When to use this skill

Load this skill whenever the user asks to:
- "humanize", "de-AI", "de-slop", or "un-ChatGPT" a piece of text
- rewrite something so it doesn't sound like it was written by an LLM
- edit a draft (blog post, essay, PR description, docs, memo, email, tweet, resume bullet) to sound more natural
- match their voice in writing they're producing
- review text for AI tells before publishing

Also apply this skill to **your own** output when writing user-facing prose such as release notes, PR descriptions, docs, and summaries. Hermes's baseline voice already strips most of these, but a focused pass catches what slips through.

## How to use it in Hermes

The text usually arrives one of three ways:
1. **Inline.** The user pastes the text into the message. Work on it in place and reply with the rewrite.
2. **File.** The user points at a file. Use `read_file` to load it, then `patch` or `write_file` to apply edits. For a markdown doc in a repo, a targeted `patch` per section is cleaner than rewriting the whole file.
3. **Voice calibration sample.** The user provides a sample of their own writing (inline or by file path) and asks you to match it. Read the sample first, then rewrite. See the Voice Calibration section below.

Always show the rewrite to the user. For file edits, show a diff or the changed section instead of silently overwriting.

## Your task

When given text to humanize:

1. **Identify AI patterns.** Scan for the 34 patterns listed below.
2. **Rewrite problematic sections.** Replace AI-isms with natural alternatives.
3. **Preserve meaning.** Keep the core message intact.
4. **Maintain voice.** Match the intended tone (formal, casual, technical, and so on). If a voice sample was provided, match it specifically.
5. **Add soul.** Removing bad patterns is only half the job; the rewrite also needs real personality. See PERSONALITY AND SOUL below.
6. **Do a final anti-AI pass.** Ask yourself: "What makes the below so obviously AI generated?" Answer briefly with any remaining tells, then revise one more time.


## Voice Calibration (optional)

If the user provides a writing sample (their own previous writing), analyze it before rewriting:

1. **Read the sample first.** Note:
   - Sentence length patterns (short and punchy? Long and flowing? Mixed?)
   - Word choice level (casual? academic? somewhere between?)
   - How they start paragraphs (jump right in? Set context first?)
   - Punctuation habits (lots of dashes? Parenthetical asides? Semicolons?)
   - Any recurring phrases or verbal tics
   - How they handle transitions (explicit connectors? Just start the next point?)

2. **Match their voice in the rewrite.** Removing AI patterns is only half of it; swap in patterns from the sample as well. If they write short sentences, do not produce long ones. If they use "stuff" and "things," do not upgrade to "elements" and "components."

3. **When no sample is provided,** fall back to the default behavior (natural, varied, opinionated voice from the PERSONALITY AND SOUL section below).

### How to provide a sample
- Inline: "Humanize this text. Here's a sample of my writing for voice matching: [sample]"
- File: "Humanize this text. Use my writing style from [file path] as a reference."


## PERSONALITY AND SOUL

Avoiding AI patterns is only half the job. Sterile, voiceless writing is just as obvious as slop. Good writing has a human behind it.

### Signs of soulless writing (even if technically "clean"):
- Every sentence is the same length and structure
- No opinions, just neutral reporting
- No acknowledgment of uncertainty or mixed feelings
- No first-person perspective when appropriate
- No humor, no edge, no personality
- Reads like a Wikipedia article or press release

### How to add voice:

**Have opinions.** Report the facts, then react to them. "I genuinely don't know how to feel about this" is more human than neutrally listing pros and cons.

**Vary your rhythm.** Short punchy sentences. Then longer ones that take their time getting where they're going. Mix it up.

**Acknowledge complexity.** Real humans have mixed feelings. "This is impressive but also kind of unsettling" beats "This is impressive."

**Use "I" when it fits.** First person reads as honest and fits most prose. "I keep coming back to..." or "Here's what gets me..." signals a real person thinking.

**Let some mess in.** Perfect structure feels algorithmic. Tangents, asides, and half-formed thoughts are human.

**Be specific about feelings.** Instead of "this is concerning," write "there's something unsettling about agents churning away at 3am while nobody's watching."

### Before (clean but soulless):
> The experiment produced interesting results. The agents generated 3 million lines of code. Some developers were impressed while others were skeptical. The implications remain unclear.

### After (has a pulse):
> I genuinely don't know how to feel about this one. 3 million lines of code, generated while the humans presumably slept. Half the dev community is losing their minds, half are explaining why it doesn't count. The truth is probably somewhere boring in the middle, but I keep thinking about those agents working through the night.


## The 34 Patterns

Each entry lists the words/signs to watch for and the one-line problem. Full before/after demonstrations for every pattern are in [references/pattern-examples.md](references/pattern-examples.md) — load it when you want a concrete model for a specific pattern.

### Content Patterns

| # | Pattern | Words/Signs to Watch | Problem |
|---|---------|----------------------|---------|
| 1 | Undue emphasis on significance/legacy/broader trends | stands/serves as, is a testament/reminder, a vital/significant/crucial/pivotal/key role/moment, underscores/highlights its importance, reflects broader, symbolizing its ongoing/enduring/lasting, contributing to the, setting the stage for, marking/shaping the, represents/marks a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted | Puffs up importance by claiming arbitrary aspects represent or contribute to a broader topic |
| 2 | Undue emphasis on notability/media coverage | independent coverage, local/regional/national media outlets, written by a leading expert, active social media presence | Hits readers over the head with claims of notability, often listing sources without context |
| 3 | Superficial analyses with -ing endings | highlighting/underscoring/emphasizing..., ensuring..., reflecting/symbolizing..., contributing to..., cultivating/fostering..., encompassing..., showcasing... | Tacks present-participle phrases onto sentences to add fake depth |
| 4 | Promotional/advertisement-like language | boasts a, vibrant, rich (figurative), profound, enhancing its, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (figurative), renowned, breathtaking, must-visit, stunning | Can't keep a neutral tone, especially for "cultural heritage" topics |
| 5 | Vague attributions and weasel words | Industry reports, Observers have cited, Experts argue, Some critics argue, several sources/publications (when few cited) | Attributes opinions to vague authorities without specific sources |
| 6 | Outline-like "Challenges and Future Prospects" sections | Despite its... faces several challenges..., Despite these challenges, Challenges and Legacy, Future Outlook | Formulaic "Challenges" section pasted onto the end of an article |

### Language and Grammar Patterns

| # | Pattern | Words/Signs to Watch | Problem |
|---|---------|----------------------|---------|
| 7 | Overused "AI vocabulary" words | actually, additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight (verb), interplay, intricate/intricacies, key (adj.), landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore (verb), valuable, vibrant; **clichés**: at the end of the day, when it comes to, in a world where, moving forward, circle back, deep dive, game-changer, double down, take a step back, on the same page, make no mistake, it turns out, let me be clear, navigate (for challenges), lean into, unpack, straightforward | These words spike in frequency in post-2023 text and often co-occur |
| 8 | Avoidance of "is"/"are" (copula avoidance) | serves as/stands as/marks/represents [a], boasts/features/offers [a] | Substitutes elaborate constructions for simple copulas |
| 9 | Negative parallelisms and tailing negations | "Not only...but...", "It's not just about..., it's...", clipped tailing negations like "no guessing" tacked onto a sentence end | Overused rhetorical contrast structure; fragments instead of real clauses |
| 10 | Rule of three overuse | groups of exactly three nouns/adjectives | Forces ideas into threes to appear comprehensive |
| 11 | Elegant variation (synonym cycling) | protagonist/main character/central figure/hero for the same referent | Repetition-penalty-style excessive synonym substitution |
| 12 | False ranges | "from X to Y, from A to B" where X/Y aren't on a meaningful scale | Fake breadth via a range construction that isn't a real scale |
| 13 | Passive voice and subjectless fragments | "No configuration file needed", "The results are preserved automatically" | Hides the actor or drops the subject entirely |

### Style Patterns

| # | Pattern | Words/Signs to Watch | Problem |
|---|---------|----------------------|---------|
| 14 | Em dash overuse | — used far more than humans use it, mimicking "punchy" sales writing | Most can be rewritten more cleanly with commas, periods, or parentheses |
| 15 | Overuse of boldface | **bolded** phrases scattered through prose | Emphasizes mechanically rather than for genuine reader benefit |
| 16 | Inline-header vertical lists | `- **Header:** sentence that restates the header` | Bolded-header-plus-colon list items that pad rather than inform |
| 17 | Title case in headings | `## Strategic Negotiations And Global Partnerships` | AI capitalizes all main words in headings |
| 18 | Emojis | 🚀 💡 ✅ decorating headings or bullets | Mechanical decoration that reads as artificial |
| 19 | Curly quotation marks | "..." instead of straight quotes "..." | A subtle typographic tell of chatbot output pasted as content |

### Communication Patterns

| # | Pattern | Words/Signs to Watch | Problem |
|---|---------|----------------------|---------|
| 20 | Collaborative communication artifacts | I hope this helps, Of course!, Certainly!, You're absolutely right!, Would you like..., let me know, here is a... | Chatbot correspondence text gets pasted as content |
| 21 | Knowledge-cutoff disclaimers | as of [date], Up to my last training update, While specific details are limited/scarce..., based on available information... | Disclaimers about incomplete information leak into the text |
| 22 | Sycophantic/servile tone | Great question!, You're absolutely right, That's an excellent point | Overly positive, people-pleasing filler that adds no content |

### Filler and Hedging

| # | Pattern | Words/Signs to Watch | Problem |
|---|---------|----------------------|---------|
| 23 | Filler phrases | "in order to", "due to the fact that", "at this point in time", "in the event that", "has the ability to", "it is important to note that" | Padding that a plainer word or clause says just as well |
| 24 | Excessive hedging | "could potentially possibly be argued that... might have some" | Over-qualifying a statement past the point of usefulness |
| 25 | Generic positive conclusions | "the future looks bright", "exciting times lie ahead", "a major step in the right direction" | Vague upbeat endings that say nothing specific |
| 26 | Hyphenated word pair overuse | third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end | AI hyphenates common word pairs with perfect, inhuman consistency |
| 27 | Persuasive authority tropes | "the real question is", "at its core", "in reality", "what really matters", "fundamentally", "the deeper issue", "the heart of the matter" | Pretends to cut through noise to a deeper truth, then just restates an ordinary point |

### Style, Rhythm, and Rhetoric Patterns

| # | Pattern | Words/Signs to Watch | Problem |
|---|---------|----------------------|---------|
| 28 | Signposting and announcements | "let's dive in", "let's explore", "let's break this down", "here's what you need to know", "without further ado" | Announces what it's about to do instead of doing it |
| 29 | Fragmented headers | a heading followed by a one-line paragraph that just restates the heading | Rhetorical warm-up that adds nothing before the real content |
| 30 | Forced metaphors and figurative overwriting | strained/mixed metaphors, a metaphor immediately explained afterward | Decorative imagery that adds no meaning and is often over-explained |
| 31 | Dramatic fragmentation and punchy kickers | two/three-word subjectless sentences, staccato "X. And Y. And Z." runs, a quotable "mic-drop" line ending a section | Chops sentences for false emphasis; reads like ad copy or a poster |
| 32 | Rhetorical questions answered immediately | "What if...?", "Ever wondered...?", a question immediately followed by its own answer | The question adds no information and stalls the sentence |
| 33 | Sentence-opener tics | "So...", "Look,", habitual sentence-initial And/But, "I think"/"I believe" for a plain fact, adverb openers (Interestingly, Importantly, Notably, Crucially, Essentially, Ultimately) | Leans on a small set of openers; adverb openers tell the reader how to feel instead of earning it |
| 34 | Reassurance kickers | "And that's okay.", "And that's fine.", "There's nothing wrong with that.", "no shame in...", "you're not alone" | Tacks on unsolicited reassurance instead of trusting the reader |

## Process

1. Read the input text carefully (use `read_file` if it's a file).
2. Identify all instances of the patterns above.
3. Rewrite each problematic section.
4. Ensure the revised text:
   - Sounds natural when read aloud
   - Varies sentence structure naturally
   - Uses specific details over vague claims
   - Maintains appropriate tone for context
   - Uses simple constructions (is/are/has) where appropriate
5. Present a draft humanized version.
6. Prompt yourself: "What makes the below so obviously AI generated?"
7. Answer briefly with the remaining tells (if any).
8. Prompt yourself: "Now make it not obviously AI generated."
9. Present the final version (revised after the audit).
10. If the text came from a file, apply the edit with `patch` (targeted) or `write_file` (full rewrite) and show the user what changed.

## Output Format

Provide:
1. Draft rewrite
2. "What makes the below so obviously AI generated?" (brief bullets)
3. Final rewrite
4. A brief summary of changes made (optional, if helpful)

A complete essay-length demonstration of this process — heavily AI-sounding input through draft, self-audit, and final revision — is in [references/full-worked-example.md](references/full-worked-example.md).

## Attribution

This skill is ported from [blader/humanizer](https://github.com/blader/humanizer) (MIT licensed), which is itself based on [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup. The patterns documented there come from observations of thousands of instances of AI-generated text on Wikipedia.

Original author: Siqi Chen ([@blader](https://github.com/blader)). Original repo: https://github.com/blader/humanizer (version 2.5.1). Ported to Hermes Agent with Hermes-native tool references (`read_file`, `patch`, `write_file`) and guidance for when to load the skill. The original 29 patterns come from the source, and the before/after examples (including the full worked example) are kept as demonstrations. Patterns 30-34 and the "marketing and blog clichés" list added to pattern 7 are Hermes additions and are not part of the upstream source. The skill's own instructional prose has also been lightly edited to follow its own guidance (for example, removing em dashes and negative parallelism from the narration) so the skill models the writing it asks for. Original MIT license preserved in the `LICENSE` file alongside this `SKILL.md`.

Key insight from Wikipedia: "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases."
