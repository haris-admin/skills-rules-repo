---
name: amlhive-blog-linkedin-push
description: Turn one AMLHive compliance-blog article into a three-part LinkedIn push — an AMLHive company-page post, Alveena Haris's personal founder post, and a Haris-voiced image-carousel generation request/brief — saved together in a dated campaign folder. Use when asked to "add a LinkedIn post for the AMLHive/Alveena/Haris accounts" for a specific article, to prepare a carousel request, or to run today's blog-article social push.
---

# AMLHive Blog → LinkedIn Push

**Canonical source: `skills-rules-repo/content-growth-and-media/amlhive-blog-linkedin-push/SKILL.md`
(`~/code/github/haris-admin/skills-rules-repo`).** This copy is a local mirror for this project.
The two must never drift — if you edit either copy, copy the change to the other one in the same
session and re-run `skills-rules-repo`'s `scripts/validate.py` + `scripts/generate_catalog.py`
before finishing. Do not treat "it works from wherever I edited it" as sufficient; a second,
silently-diverged copy is exactly the duplication problem this note exists to prevent (see the
17-18 Sep 2026 incident below, where a second skill was independently created covering the same
job before this rule was written down).

## Purpose

Given one AMLHive compliance-blog article (live or staged for publish), produce three
ready-to-use LinkedIn deliverables in a single dated file, without duplicating or silently
conflicting with any campaign material that already exists for that article. This is a narrower,
blog-article-specific companion to `amlhive-social-media` (the general six-platform workflow) —
read that skill's `references/claim-and-citation-judge.md` and
`docs/outreach/social-account-registry.md` before drafting; this skill governs the *shape* of the
LinkedIn deliverables and the folder convention, not the platform rules those already cover.

## Required context

1. `docs/outreach/brand_voice.md` — locked taglines, LinkedIn-Specific Rules (hook-line discipline,
   hashtag limit, emoji limit, first-comment link convention for personal posts, no
   self-congratulation opener).
2. `docs/outreach/social-account-registry.md` — confirms which LinkedIn identity is which: AMLHive
   company Page, Alveena Haris (founder/personal perspective), Haris Habib (user-designated human
   voice for founder/personal posts — confirm which of Alveena's or Haris's account a given push
   actually targets; do not assume).
3. `docs/outreach/linkedin/post_launch_posts.md` — the worked precedent for personal-vs-company
   posting order and the first-comment link convention. Follow its shape.
4. `docs/branding.md` / `docs/brand_colours.md` — colour/typeface truth for anything a carousel
   brief specifies visually. Never use `docs/outreach/canva_branding_guidelines_draft_2026-09-17.md`'s
   colour or font recommendations (see that file's reconciliation table).
5. The target article's own bundle — `assets/blog-migration/<slug>/post.md`, `claim-register.md`
   if present, and its `social/` folder. **Always check `social/` for existing campaign material
   first** (a `creative-brief.md`, `haris-linkedin-video.md`, or prior `linkedin.md`) — this
   article may already have a different, more developed campaign in flight. Flag it in the new
   file rather than silently building a second, conflicting treatment.

## Workflow

1. **Confirm the article's real publication state before drafting anything that links to it.**
   Local `meta.json`/tracking docs can be stale — a status of `draft` does not prove the article
   isn't actually live, and vice versa (same failure mode as
   `docs/agent_rules/../feedback-openspec-status-drift-both-ways` for code). Do a read-only fetch
   of the expected public URL. If it's live, correct any stale `publication_state` in `meta.json`
   and the CMS handoff doc (`assets/blog-admin-cms-publishing-instructions.md`) in the same pass —
   don't leave the drift for someone else to rediscover. If it isn't live yet, every deliverable
   below must say so explicitly and warn against posting/building before the CMS post exists.

2. **Pull the exact facts the deliverables will use from the article's own body**, not from
   memory or from whatever brief the human supplied — cross-check any statistic, source citation
   or regulatory claim against `post.md` (and `claim-register.md`/`source-notes.md` where they
   exist) before using it in a caption or carousel slide. If the human supplies ready-made slide
   copy (as in the worked example below), verify it against the article rather than assuming it's
   already correct — a small independent check is cheap and this repo's whole content pipeline is
   built around never shipping an unverified claim.

3. **Draft the three deliverables:**
   - **AMLHive company page post** — link in the post body (tracked URL, `utm_source=linkedin&
     utm_medium=organic_social&utm_campaign=<slug-topic>_<mon>_<year>&utm_content=amlhive_company`).
     Educational/value-led tone, ≤3 hashtags at the end
     (`#AustralianRealEstate #AUSTRAC #AMLCompliance`), no more than one CTA.
   - **Alveena's (or Haris's, per the registry) personal post** — founder voice, first-person,
     hook line 1, no link in the body — the tracked URL goes in a separate **first comment**
     block (`utm_content=alveena_founder` or `haris_founder`). Full value must already be in the
     post body; the link supplies depth/evidence, never the missing answer (this is a real rule,
     not a formatting preference — see `brand_voice.md` § LinkedIn-Specific Rules #5-6).
   - **Image-carousel generation request** — a *handoff brief*, not a post: the literal message
     the founder would send to whoever/whatever actually builds the carousel (Canva, an
     image-gen pipeline, a designer). Format:
     ```
     I'm generating a slideshow for LinkedIn using this article. Check this article as well and
     these are the slide directions for the slides as an image carousel.

     <article URL>

     Slide 1 — Hook
     Headline: "..."
     Sub: "..."
     Visual: ...
     Footer: "Haris Habib | AMLHive"

     Slide 2 — ...
     Title: "..."
     Bullets:
     "..."
     Small source line: "..."
     Visual: ...

     Slide N — Close
     Title / Callout box: "..."
     Footer CTA: "Read the full blog: amlhive.com.au"
     ```
     3-5 slides is typical: a hook, one or two content/context slides, and a close slide with a
     callout box and footer CTA. Add a **separate "Verification notes" block after the brief**
     (not inside it) recording exactly which claims were checked against the article and a brand
     reminder (tokens/typefaces from `docs/brand_colours.md`/`docs/branding.md`, not generic
     clip-art or stock icon language).

     **If the human names an actual build tool (e.g. "we'll use Canva")**, the generic brief above
     isn't the final deliverable — write the tool-specific production spec instead, in the same
     shape as an existing precedent if one exists for that article
     (`assets/blog-migration/<slug>/social/creative-brief.md` is the established Canva-brief shape:
     construction/colour spec, a page-by-page table of on-image copy + composition + alt text +
     evidence, image-treatment rules, a claim/source table, and a visual QA checklist — copy an
     existing one's structure rather than reinventing it). That detailed brief belongs in the
     **article's own `blog-migration/<slug>/social/` bundle**, not in the dated campaign folder,
     which stays a thinner index.

     **The post-wrapper file (`haris-linkedin-carousel.md` / the `haris-linkedin-video.md` shape)
     is the single document the human actually works from end-to-end — it must be self-contained,
     not a pointer.** Don't make them cross-reference `creative-brief.md` for the pieces they'll
     actually use while building and posting. It needs, inline, in this order:
     1. **Header block** — state/account/media/link/classification/planned date. Use this exact
        3-state model for `State`, converged on independently by two agents (Claude Code and
        Gemini Antigravity, 17-18 Sep 2026) building the same file from different directions:
        `VARIANTS_DRAFTED` (copy and build brief written, claims not yet independently judged) →
        `APPROVAL_REQUIRED` (all claims verified, the founder has read the caption, QA checklist
        complete) → `PUBLISHED` (posted; date and URL recorded). Never move to `APPROVAL_REQUIRED`
        without the founder having personally confirmed the caption text, and never to `PUBLISHED`
        without the article being live at the linked URL.
     2. **Canva build status and fix instructions** — what's already built (design name, where to
        find it), what's broken and exactly how to fix it, the colour hex reference, and the
        page-by-page table (copy this in from `creative-brief.md`, don't just cite it) with columns
        **Page / Headline-or-on-image-copy / Layout notes / Alt text / Evidence-source** — alt text
        written per page, ready to paste into LinkedIn's alt-text field, not left blank; the
        evidence column names the `source-notes.md` item number it traces to.
        For a first-time build (nothing built yet), this section is the generation brief instead —
        same content, framed as "build this" rather than "fix this." If any claim in the table
        isn't yet verified, mark that row `UNVERIFIED — do not post` and do not write the caption
        section until it's resolved — don't draft copy around an unconfirmed claim.
     3. **A pre-export QA checklist**, including: article confirmed live before any posting, logo
        unstretched, the personal byline (`<Founder Name> | AMLHive`) present on page 1 only (the
        AMLHive company carousel omits it — don't confuse the two conventions), contrast rule
        respected, no hashtags rendered on any slide, alt text supplied per page on upload.
     4. **The final, ready-to-post caption and first-comment link, written out in full** — not "see
        `creative-brief.md`." This is the part most likely to get missed if it's left as a
        cross-reference, because it's needed at a completely different time (after the images are
        fixed, days later) than the build instructions (needed while sitting in Canva right now) —
        by the time the human returns for the caption, a "see the other file" pointer is exactly
        the kind of thing that gets skipped. One file, everything needed at both moments. Caption
        rules for a personal post: first person in the founder's own voice (not AMLHive marketing
        voice), opens with the article's central scenario/insight not a promotional hook, no link
        in the body, ≤3 hashtags at the very end only, and the caption must stand alone — a reader
        who never swipes the carousel should still get full value from the text alone.
     5. **Claim review record** — a table with columns **Claim surface / Source / Verified /
        Reviewer / Date**. A claim counts as verified only when traced to a primary source with a
        retrieval date; an article-text summary alone doesn't count.
     6. **The step-by-step posting handoff**, spelled out in order so the founder needs nothing
        else: open Canva and export the pages using §2/§3 above → create the LinkedIn post and
        attach the exported images as a carousel → paste the §4 caption into the post body (no
        link) → publish → immediately add the §4 first-comment URL.

     `creative-brief.md` still exists alongside it as the deeper technical/evidence record
     (full claim/source table with retrieval detail, image-treatment rules for anyone building
     future variants) — but it's a reference document now, not something the human needs open
     while actually doing the work. If a generic brief was already saved in the dated folder
     before the tool was named, mark it superseded and point to the real one rather than deleting
     it.

     **Do not create a second, narrower skill for this** (e.g. a per-founder or per-platform
     variant) — extend this skill's carousel section instead. Two skills independently converged
     on the same self-contained-file design 17-18 Sep 2026 (this one, and a short-lived
     `haris-linkedin-carousel` skill Gemini Antigravity created covering only the Haris case) —
     the narrower one was merged into this section and retired rather than kept alongside it,
     specifically to prevent exactly this kind of duplication recurring.

4. **Save all three together** in one file:
   `assets/social-campaigns/YYYY-MM-DD-<article-slug>/social-drafts.md`, dated to the day the push
   is being prepared (not the article's original publish date if that differs — the folder name
   tracks when this social push was built). This is a **going-forward convention** — do not rename
   existing `assets/blog-migration/<slug>/` bundles or their `social/` subfolders to match; those
   stay as the article's own production bundle. If the article's blog-migration bundle already has
   its own `social/linkedin.md` (company) or a personal post that satisfies a guard test
   (`frontend/tests/unit/<slug>-blog.test.ts` often asserts these paths exist), don't move or
   duplicate-edit those — copy the same content into the new dated file for a consolidated view,
   and note where the single source of truth actually lives.

5. **Never claim anything is posted, scheduled or approved.** Every deliverable is a draft
   awaiting the account owner's same-run approval per `amlhive-social-media`'s state model — write
   the file, don't post from it.

## Common failure modes (from the 17 Sep 2026 session this skill was extracted from)

- Building a second carousel campaign for an article that already has one in flight
  (`VARIANTS_DRAFTED` or further) without checking `social/` first — wastes production time and
  risks two visually different carousels going out for the same post.
- Treating a human-supplied slide brief as already correct — always cross-check its stats/claims
  against the actual article before formalising it.
- Posting a personal-account link in the post body instead of the first comment (or vice versa
  for the company page) — the two accounts have opposite conventions, both documented in
  `docs/outreach/linkedin/post_launch_posts.md`.
- Drafting posts/briefs that link to an article before confirming it's actually live — check the
  real URL, don't trust local `meta.json`/handoff-doc status alone (it drifts).
- **A delegated Canva build following the brief's copy exactly can still ship with major visual
  gaps** — a real build this session got every page's text right but had two pages with text
  overflowing the canvas into the footer byline (unreadable), and was missing every specified
  colour accent, the logo lockup, and the closing footer bar, none of which showed up in the
  build's own completion summary. **Always open and look at the actual exported image files
  yourself before treating a Canva build as done** — see `amlhive-canva-assets`'s Visual QA
  section for what to check specifically. If delegating the Canva build to a subagent, budget for
  a second pass; a first pass getting the text/claims right but the visual polish wrong is the
  expected outcome, not a sign something went badly.
- Plus Jakarta Sans doesn't exist in Canva's font library — see `amlhive-canva-assets`'s "Known
  drift" section for the Poppins substitute, so this doesn't need re-discovering per carousel.
