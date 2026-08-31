# AI Tells, Reframed as Growth Opportunities

These are the Wikipedia "Signs of AI writing" categories. We do NOT use them to judge "is this AI". We use them to spot where a passage is **doing less work than it could** and to show the student a stronger move in their own voice. A tell present in a student's Tier 3 writing is not evidence of cheating; it is a place the argument can get sharper. Pair every item here with the matching move in `voice-development.md`.

Framing flip: instead of "cut this to evade detection", every rule reads "here is a weak move many writers make, here is why it weakens the argument, here is a stronger version".

---

## 1. Regression to the mean (specificity collapse)

**What it is.** Specific, unusual, load-bearing facts get smoothed into generic, positive descriptions that could apply to almost anything. The subject becomes simultaneously less specific and more exaggerated.

**Sign.** A precise, load-bearing detail (the actual invention, date, mechanism) is replaced by an abstract superlative.
- Weak: "a revolutionary titan of industry".
- Strong: "the inventor of the first automatic train-coupling device (1873)".

**What good academic writing does instead.** It keeps the precise, unusual detail. Specificity IS the value; do not let it collapse into a superlative.

**Coaching reframe.** "Your sentence is carrying a general claim where it could carry a specific one. What is the exact fact underneath it?"

---

## 2. Undue emphasis on significance, legacy, and broader trends

**What it is.** The writing puffs up importance by asserting the topic represents or contributes to some broader trend, often with a recognisable repertoire of phrasings, sometimes after a hedging preamble that admits low importance then asserts importance anyway.

**Words and phrases to watch.** stands/serves as; is a testament/reminder; a vital/significant/crucial/pivotal/key role; underscores/highlights its importance; reflects broader; symbolizing its ongoing/enduring/lasting; contributing to the; setting the stage for; marking/shaping the; represents/marks a shift; key turning point; evolving landscape; focal point; indelible mark; deeply rooted.

**Sign.** A clause is inserted asserting the topic marks a pivotal moment or a broader trend, without a source.
- Weak: "founded in 1989, marking a pivotal moment in the evolution of regional statistics".
- Strong: "founded in 1989" - and let sourced context carry any significance.

**What good academic writing does instead.** States the fact and lets significance emerge from sourced evidence; it does not editorialise about pivotal moments or enduring legacies without attribution.

**Coaching reframe.** "This sentence tells the reader the thing is important. Stronger academic writing shows it with evidence and lets the reader conclude it. What is your evidence?"

---

## 3. Conservation-status / broader-ecosystem padding (genre-specific, biology)

**What it is.** For species or systems, the writing belabours conservation status or ecosystem connections even where the status is unknown and no efforts exist.

**Sign.** A generic ecosystem-health or conservation clause appended to a subject that has no such documented status.
- Weak: "there is no specific assessment, however the general health of the ecosystem is crucial for the survival of this species".
- Strong: state what IS documented; if status is unknown, say it is unknown and stop.

**What good academic writing does instead.** Reports only documented status; "unknown" is a complete and honest answer.

**Coaching reframe.** "You have added a significance clause that the sources do not support. The honest version is shorter. What do the sources actually say about status?"

---

## How to use these without harming the student

- A tell is a prompt for a question, never an accusation.
- Never say or imply "this looks AI-generated". The provenance log already says what tier each span is; you do not infer it from tells.
- One or two tells per pass, the highest-leverage ones. Do not list every tell in a passage; that is overwhelming and punitive.
- See `detector-methods-and-fairness.md` for the false-positive boundary: many of these surface patterns are ALSO legitimate human and L2 markers, so they are coaching prompts, not verdicts.


---

## Additional categories from the full Wikipedia guide

These were extracted from the source PDF and complete the ruleset above. Same framing: a prompt for a question, never a verdict.

### Canned emphasis on notability, attribution, and media coverage

LLMs act as if the best way to prove a subject is notable is to hit readers over the head with claims of notability - listing the sources a subject has been covered in and specifying source types (trade publications, regional media). They often inaccurately attribute their own superficial analyses to those sources, and echo the exact wording of Wikipedia's guidelines (e.g. 'independent coverage', 'significant, substantial, secondary coverage'). More common in 2025+ tools. On Wikipedia specifically, LLMs painstaking...

**Words and phrases to watch.** independent coverage; local/regional/national/[country name] media outlets; music/business/tech outlets; profiled in; written by a leading expert; active social media presence; maintains a strong digital presence; significant, substantial, secondary coverage; repeated national media coverage; recognised by universities.

- Weak: 'The subject has been profiled in multiple high-quality, independent, and widely-read outlets... These sources provide significant, substantial, secondary coverage, not trivial mentions or press releases.'
- Stronger: Strong writing cites sources via inline references and lets the reader judge; it does not argue notability inside the article body or parrot guideline vocabulary.

### Superficial analyses

AI chatbots insert superficial analysis of information, often relating to its significance, recognition, or impact, by attaching a present participle ('-ing') phrase at the end of sentences, sometimes with vague attributions to third parties. On Wikipedia these are usually synthesis or unattributed opinions. Newer RAG chatbots may attach these statements to named sources regardless of whether those sources say anything close.

**Words and phrases to watch.** highlighting/underscoring/emphasizing ...; ensuring ...; reflecting/symbolizing ...; contributing to ...; cultivating/fostering ...; encompassing ...; valuable insights; align/resonate with.

- Weak: '...the population of Douera stood at approximately 56,998 inhabitants, creating a lively community within its borders... further enhancing its significance as a dynamic hub of activity and culture.'
- Stronger: Strong academic prose ends sentences on the fact, not on an interpretive participial flourish; analytical claims are attributed and verifiable, not bolted on as decoration.

### Promotional and advertisement-like language

LLMs have serious problems keeping a neutral tone. Even when prompted for encyclopedic style, output tends toward advertisement-like or travel-guide prose. Can happen when generating new text or rewriting (an edit summary may claim it 'removed promotional tone' while introducing it). Subtypes: cultural-heritage importance reminders; press-release/commercial tone for people and companies. Note: not all promotional writing is AI; LLMs over-use the same set of promotional phrases regardless of topic; older LLMs (GPT-4...

**Words and phrases to watch.** boasts a; vibrant; rich; profound; enhancing; showcasing; exemplifies; commitment to; natural beauty; nestled; in the heart of; groundbreaking; renowned; featuring; diverse array.

- Weak: 'Nestled within the breathtaking region of Gonder in Ethiopia, Alamata Raya Kobo stands as a vibrant town with a rich cultural heritage and a significant place... offers visitors a fascinating glimpse into the diverse tapestry of Ethiopia... a town worth visiting.'
- Stronger: Neutral encyclopedic writing describes location and facts without adjectives of allure ('breathtaking', 'vibrant', 'worth visiting') or reader-directed selling.

### Vague attributions and overgeneralization of opinions

AI chatbots attribute opinions or claims to a vague authority (weasel wording). They also exaggerate the quantity of sources: presenting one or two sources' views as widely held, mentioning multiple 'reviewers' or 'scholars' while citing only one, or implying lists of examples are non-exhaustive ('such as') when sources give no indication other examples exist.

**Words and phrases to watch.** Industry reports; Observers have cited; Experts argue; Some critics argue; several sources/publications (when only a few are cited); such as (before exhaustive word lists); according to [nationality] sources; described in scholarship; modern researchers treat; researchers and conservationists.

- Weak: 'Due to its unique characteristics, the Haolai River is of interest to researchers and conservationists.'
- Stronger: Academic writing names the specific source or study making the claim; if no source exists, the claim is dropped, not laundered through 'researchers'.

### Outline-like conclusions about challenges and future prospects

Many LLM articles include a 'Challenges' section beginning 'Despite its [positive words], [subject] faces challenges...' and ending with a vaguely positive assessment or speculation about how ongoing/potential initiatives could benefit the subject. Often appears at the end of articles with rigid outline structure, sometimes with a separate 'Future Prospects' section. The sign is the rigid formula, not the mere mention of challenges.

**Words and phrases to watch.** Despite its... faces several challenges...; Despite these challenges; Challenges and Legacy; Future Outlook; faces new challenges and opportunities; adapt to these emerging trends; continues to thrive; positions them as critical components.

- Weak: 'Despite its industrial and residential prosperity, Korattur faces challenges typical of urban areas... With its strategic location and ongoing initiatives, Korattur continues to thrive as an integral part of the Ambattur industrial zone.'
- Stronger: Human academic writing discusses specific, sourced challenges where relevant and does not append a templated optimistic coda or speculative 'future' section.

### Leads treating Wikipedia lists or broad article titles as proper nouns

In AI-generated articles whose title is not a proper name (e.g. a list or a broad descriptive title), the first sentence introduces or defines the title as if it were a standalone real-world entity, in an unnatural way.

**Words and phrases to watch.** [Title] refers to; [Title] is the chronological list of; [Title] is a curated compilation of.

- Weak: 'EuroGames editions is the chronological list of the biennial EuroGames...' / 'The "List of songs about Mexico" is a curated compilation of musical works...'
- Stronger: Strong leads introduce the topic naturally (e.g. 'This is a list of...' or describing the subject area) rather than reifying the page title as a defined proper noun.

### High density of AI vocabulary words

LLMs overuse a specific set of words, which began appearing far more frequently in text produced after 2022. They co-occur - where there is one, there are likely others. One or two may be coincidental, but an edit (post-2022) introducing many of them, many times, is one of the strongest tells. Distribution varies by model and era. Take literally: a word being overused does NOT imply its synonyms are; and keep context in mind (e.g. 'underscore' can mean a literal underline or incidental music). When writing comments...

**Words and phrases to watch.** Additionally (esp. beginning a sentence); align with; boasts (meaning 'has'); bolstered; crucial; delve; emphasizing; enduring; enhance; fostering; garner; highlight (as a verb); interplay; intricate/intricacies; key (as an adjective); landscape (as an abstract noun); meticulous/meticulously; pivotal; robust; showcase; tapestry (as an abstract noun); testament; underscore (as a verb); valuable; vibrant; concrete (as an adjective, in comments).

- Weak: 'Somali cuisine is an intricate and diverse fusion... drawing from the rich tapestry... This culinary tapestry is a direct result of Somalia's longstanding heritage of vibrant trade... An enduring testament to the influence of Italian colonial rule... showcasing how these dishes have integrated... Additionally, Somali merchants played a pivotal role...'
- Stronger: Human academic writing draws on a far wider, topic-appropriate vocabulary and does not repeatedly reach for the same dozen abstract approval-words; era-specific clusters are absent in pre-2023 text.

### Avoidance of basic copulatives (is/are phrases)

LLM text replaces simple copular constructions using 'is'/'are' with 'serves as a', 'mark the', etc. Observed in GPT and Gemini. One study found a >10% decrease in 'is'/'are' in academic writing in 2023. LLMs also prefer marketing-related verbs (features, offers) over the neutral synonym 'has'. Sometimes more elaborate, e.g. 'ventured into politics as a candidate' vs 'was a candidate'. Especially visible in AI copyedits that 'improve' text this way. In lead sentences, LLMs sometimes avoid 'is' by writing 'refers to...

**Words and phrases to watch.** serves as / stands as / marks / represents [a]; boasts / features / maintains / offers [a]; refers to.

- Weak: Edit changes 'is LAAA's exhibition arm... There are four individual gallery spaces' to 'serves as LAAA's exhibition space... The gallery features four separate spaces.' / 'Harian Metro was established in March 1991 and is the first...' becomes 'Harian Metro holds the distinction of being the first...'
- Stronger: Strong, plain academic prose uses simple copulas ('is', 'are', 'has') where natural; the Manual of Style accepts and often prefers these over inflated verb substitutes.

### Negative parallelisms

When LLMs describe a subject, output may seem to clear up a common misconception or retroactively challenge an incomplete/incorrect conclusion the reader might reach, contrasting it with another characteristic. Common among human writers (esp. 'myths busted' listicles) but stereotypically an AI sign. Two sub-forms: 'Not just X, but also Y' (parallel constructions with not/but/however, e.g. 'Not only... but...', 'It is not just..., it's...') and 'Not X, but Y' (explicitly stating the item doesn't possess the first c...

**Words and phrases to watch.** Not only... but also; It is not just..., it's...; is not... but...; Rather, it constitutes; no..., no..., just...; not a..., not a..., just.

- Weak: 'This choice of language is not only dismissive but also unnecessarily harsh and confrontational.' / 'Self-Portrait... constitutes not only a work of self-representation, but a visual document...'
- Stronger: Strong writing makes its point directly and positively; it does not stage a strawman misconception to knock down via not/but symmetry.

### Rule of three

LLMs overuse the 'rule of three', from 'adjective, adjective, adjective' to 'short phrase, short phrase, and short phrase'. Often used to make superficial analyses appear more comprehensive.

- Weak: '...such as tiles, metals, and plastics.' / 'For cutting drywall, plywood, and other construction materials.' / 'Used in model making, woodworking, and other craft projects.'
- Stronger: Human writing varies list length to the actual content (two items, four items, a single specific item) rather than reflexively producing balanced triads everywhere.

### Lexical diversity / elegant variation

Generative AI has a repetition-penalty mechanism discouraging it from reusing words too often, producing excessive elegant variation (synonym-swapping for the same referent). Observed comparing pre-2023 to post-2023 Wikipedia text and Wikipedia vs GPT-4o-mini/Gemini-1.5-Flash generated articles. Caveat: if a user adds multiple AI pieces in separate edits, this may not apply (each generated in isolation); and non-native English editors (e.g. taught in Italian schools to avoid repetition) may also avoid repeated word...

- Weak: For 'Soviet artistic constraints': 'the constraints of socialist realism', 'the challenging climate of Soviet artistic constraints', 'socialist realism', 'the constraints imposed by the artistic norms', 'Russian avant-garde', 'their creativity', 'diverse yet united front of non-conformist norms' - all cycling to avoid repeating terms.
- Stronger: Clear academic writing repeats a key term consistently for precision (per WP:The problem with elegant variation) rather than dressing it in ever-changing synonyms.

### Section summaries

When generating longer outputs, older LLMs often added sections titled 'Conclusion' or similar, and often ended paragraphs or sections by summarizing and restating the core idea.

**Words and phrases to watch.** In summary; In conclusion; Overall.

- Weak: 'In summary, the educational and training trajectory for nurse scientists typically involves a progression... This structured pathway ensures that nurse scientists acquire the necessary knowledge and skills...'
- Stronger: Encyclopedic articles do not editorialise with 'In summary/In conclusion' wrap-ups; each section presents information without restating itself.

### Didactic disclaimers (historical, ~2023-2024)

Older LLMs often added disclaimers about topics being 'important to note', frequently taking the form of advice to an imagined reader regarding safety or controversial topics, or disambiguating topics that vary by locale/jurisdiction. Several appear in OpenAI's GPT-4 system card as examples of 'partial refusals'.

**Words and phrases to watch.** it's important/critical/crucial to note/remember/consider; worth noting; may vary.

- Weak: 'However, it's important to note that these caucuses operate outside the formal ANC structure and their influence on policy decisions may vary.' / 'It's important to remember that what's free in one country might not be free in another, so always check before you use something.'
- Stronger: Academic writing states qualifications factually and impersonally; it does not address the reader with safety advice or 'important to note' framing.

### Canned assurance of quality, good faith, and policy adherence (comments)

AI chatbots communicate good intentions in a specific way - invoking policies, guidelines, and standards as a broad, formal, abstract whole (legalese), often using AI vocabulary. Appears in user comments rather than article content.

**Words and phrases to watch.** align(s) with Wikipedia's aim/goal(s); adhere(s) to Wikipedia's policies/guidelines/standards; I am/we are committed to ...; I assure you that ...; my intention/goal is to ....

- Weak: 'I assure you that my intentions are aligned with Wikipedia's principles of neutrality, verifiability, and reliability. I strive to adhere to all content and editing guidelines...'
- Stronger: Genuine human editors discuss the specific edit or source at hand; they rarely issue abstract loyalty oaths to the project's principles.

### Canned offers to receive constructive criticism (comments)

Expressions of willingness to take constructive criticism, very common in AI comments by users whose drafts were declined, or rarely themselves. The difference from conscientious humans becomes obvious once you actually provide the criticism.

**Words and phrases to watch.** If you have any concerns/suggestions; If there are specific sections/areas that ...; I am willing/happy to address ...; I am open to/would appreciate/welcome any additional/further input/guidance/feedback.

- Weak: 'If there are specific areas that need further attention or modification, I am more than willing to make adjustments... would be grateful for any guidance you could provide...'
- Stronger: A real editor engages with feedback already given and acts on it, rather than repeatedly offering in the abstract to receive it.

### Canned calls to focus on content instead of conduct (comments)

Users responding to AI-use accusations by denying AI use (or that Wikipedia prohibits it) and calling for discussion to instead focus solely on improving the affected articles. They ask accusers to point out which contributions have tone issues as a form of constructive criticism. When told their editing pattern is disruptive, they dismiss the accusation as speculative/unfounded/baseless and accuse critics of being uncivil, hostile, aggressive; may state intent to withdraw because it has become 'emotionally charged...

**Words and phrases to watch.** accusing/accusations/accusatory; dismissing/dismissals/dismissive; instead of/rather than ...; let's focus on ....

- Weak: 'Personal attacks and accusations of AI-generated content or paid editing do not address the policy-based arguments... Instead of focusing on editor backgrounds, let's focus on whether the subject meets Wikipedia's notability guidelines...'
- Stronger: A human editor can directly confirm or explain their process and engage the specific concern; they do not deflect every query into a civility complaint.

### Wikilawyering and non-existent/misapplied policies (comments)

Selectively citing or interpreting policies, guidelines, or precedent to justify conduct even against the purpose of those policies. AI chatbots generate text affirming what the user wants to believe even when it doesn't hold up. Sub-forms: defending tagged content by demanding accusers point to specific passages; citing non-existent policies/guidelines or misattributing hallucinated ones to real shortcut pages; using non-existent shortcuts that redirect nowhere; invoking WP:PRESERVE as a catch-all anti-deletion ar...

**Words and phrases to watch.** Per WP:[shortcut]; WP:PRESERVE; WP:AISIGNS; WP:RSLOCAL; WP:LLMUSE; WP:AIASSIST; WP:AFDPURPOSE.

- Weak: 'This meets the standard for WP:RSLOCAL, which permits the use of regionally relevant sources...' (hallucinated shortcut) / handwaving toward WP:PRESERVE at AfD regardless of whether core content policies are met.
- Stronger: Experienced humans cite real, correctly-applied policies and can quote them accurately; they do not manufacture shortcuts or stretch a guideline past its stated scope.

### Confusion over the reason for a declined draft (comments)

AI chatbots cannot read the decline notice on a draft and only respond to what the user tells them. AI-generated questions about declined drafts express uncertainty or request clarification over the reason even when the decline notice is clear, sometimes producing self-contradictory comments that acknowledge the specific reason but then ask whether that was really it.

**Words and phrases to watch.** I understand the concern... I am trying to understand whether; whether the issue is mainly... or both.

- Weak: 'The latest decline says the draft needs multiple published secondary sources... I understand the concern... I am trying to understand whether the problem is mainly that these sources are not strong enough for WP:BIO/WP:NARTIST, or whether the draft structure and tone are still the main issue.'
- Stronger: A human who read the decline notice addresses the stated reason directly instead of re-litigating which of several possible reasons applied.

### Canned request for source assessment (comments)

When confronted by a declined draft or criticism, LLM editors make a stock request for an 'experienced', 'uninvolved', or 'neutral' editor to give a second opinion on their sources, carrying the (unintentional) implication that the declining reviewer didn't do their job properly. Near-identical wording recurs across unrelated users.

**Words and phrases to watch.** Could an experienced/uninvolved editor advise which of these sources count as reliable, independent, significant coverage; which should be treated only as supporting or weak sources.

- Weak: 'Could an uninvolved editor advise which of the current references, if any, count as significant independent secondary coverage for notability purposes, and which should be treated only as supporting or weak sources?' (appears nearly verbatim from different people).
- Stronger: A genuine editor engages with the reviewer who already assessed the sources, or makes a specific case for specific references, rather than issuing an identikit request.

### Formatting tells (markup, not prose)

- Title case in section headings: AI strongly tends to capitalize all main words (e.g. 'Impact of Technology and Digitalization', 'Sustainable Development and Environmental Law') - contrary to Wikipedia's sentence-case heading convention.
- Overuse of boldface: excessive, mechanical emphasis - bolding every instance of a chosen word/phrase in a 'key takeaways' fashion, inherited from readmes, fan wikis, how-tos, sales pitches, slide decks, listicles.
- Inline-header vertical lists: an ordered/unordered list where the marker (number, bullet, dash) is followed by an inline boldfaced header separated by a colon, then descriptive text (e.g. '**Route Details**: Starts at Medak...'). Markers may render as literal bullet/hyphen/en-dash characters or explicit '1.' numbers instead of proper wikitext; sometimes no punctuation separates title from text.
- Overuse of em dashes ( - ): used more often than non-professional human text of the same genre, and in places humans would use commas, parentheses, colons, or hyphens; used in a formulaic 'punched up' sales-like way to over-emphasize clauses/parallelisms. Stronger in combination with other signs; more common on discussion pages.
- Curly/typographic quotation marks (“ ”, ‘ ’) and curly apostrophes (’) instead of straight ('  ' '), often used inconsistently (mixing curly and straight in one response). Note: ChatGPT/DeepSeek use them; Gemini and Claude typically do NOT. Not proof alone (CMOS-edited works, Word smart quotes, macOS/iOS autocorrect also produce them).
- Unusual use of tables: creating unnecessary small tables that would be better as prose or an infobox (e.g. a 3-row 'Key Statistics' table, or a tiny Name/Designation management table).
- Skipping heading levels: starting sections at level 3 (===) instead of level 2 (==), against Wikipedia accessibility/style conventions - unlikely in a manually-formatted page.
- Thematic breaks before headings: inserting a horizontal rule (----, or Markdown ***/___) before each heading, common in Markdown output.
- Use of Markdown instead of wikitext: asterisks/underscores for bold/italic, # for headings (## rendered by MediaWiki as a numbered list), () around URLs, ``` fenced code blocks, --- thematic breaks; faulty wikitext mixed with Markdown is a strong tell (esp. a fenced Markdown code block containing rudimentary wikitext).
- Emoji as formatting: decorating section headings or bullet points by placing an emoji in front of them (mostly in talk-page comments and edit summaries).
- Section titles in plain text: messages broken into sections separated by lines that are clearly intended as section titles, appearing as plain text or Markdown.
- Markup/reference-bug artifacts: ChatGPT's 'turn0search0'/'turn0image0' (PUA-Unicode-wrapped), :contentReference[oaicite:0]{index=0}, oai_citation, Example+1, [attached_file:1]/[web:1] (Perplexity), grok_card / grok_render_citation_card_json (Grok), [cite: 1] (Gemini), 【85†L261-269】 lenticular-bracket/dagger markers (DeepSeek), JSON ({"attribution":{"attributableIndex":"X-Y"}}), :::writing{variant="document" id="NNNNN"} triple-colon markup.
- UTM/referrer tracking params on source URLs: ?utm_source=chatgpt.com / utm_source=openai / utm_source=copilot.com / referrer=grok.com.
- Placeholder/Mad-Libs artifacts: unfilled bracketed templates ([Your Name], [Entertainer's Name], [Describe the specific section...], INSERT_SOURCE_URL_30, PASTE_SPOTIFY_TRACK_URL_HERE) and placeholder dates like access-date=2025-XX-XX or 2022-11-XX.
- Broken wikitext / non-existent templates and categories: garbled Template:AfC submission code, hallucinated infoboxes/templates appearing as red links, hallucinated or renamed categories, {{Example}} written with curly braces causing unintended transclusion of maintenance banners.
- Citation pathologies: broken external links / 404s, invalid DOIs/ISBNs (bad checksum), DOIs leading to unrelated articles, book citations without page numbers or URLs, named references declared in <references> but unused inline (cite errors), incorrect/unconventional ref re-use syntax, ↵ used to indicate footnotes.
- Pre-placed maintenance templates: a new draft that already contains an AfC template set to 'declined' (content-free), or maintenance/protection templates that shouldn't plausibly be there.
- Email-form artifacts: 'Subject:' lines intended for an email Subject field; salutations/valedictions and letter-like framing.
- Abrupt cut-offs: text that stops mid-sentence (token limit / 'continue generating'); outdated access-date values inconsistent with edit date.

---

## Lane 1 cleaner: scrub AI CONTRIBUTIONS before the student adopts them

These concrete lists (from Wikipedia plus Will Francis, How to Stop Claude Writing Like an AI) are applied to text the AI generates (a Pre-Write scaffold, a suggested opener) BEFORE it lands in the student draft, so the AI never injects its tells into the student voice. They are NOT a scoring penalty on the student own writing (see Lane 2 below).

**Banned words (AI-overused).** delve, dive into, navigate (figurative), underscore, bolster, foster, harness, leverage, unpack, shed light on, pave the way, pivotal, groundbreaking, cutting-edge, transformative, game-changing, innovative, robust, comprehensive, seamless, intricate, nuanced (as empty praise), vibrant, multifaceted, holistic, testament, landscape (figurative), realm.

**Banned phrases.**
- In today's [fast-paced / rapidly evolving / digital] world...
- It is important / worth noting that...
- One of the most [important / significant / crucial]...
- When it comes to... / At its core... / At the end of the day...
- This is where X comes in / Let us break it down
- Plays a crucial role in... / It cannot be overstated...
- ...underscoring the importance of... / ...highlighting the need for...
- ...reflecting a broader trend toward... / ...marking a significant shift in...

**Banned structures (fake insight).**
- It is not just X, it is Y
- Not only X, but Y
- This is not about X. It is about Y.
- No X. No Y. Just Z.

**Style for AI contributions.** Use contractions. At most one em dash per passage (prefer commas or parentheses). Do not over-format with headers and bullets where prose is clearer. Drop preamble and performative enthusiasm. Vary sentence and paragraph length.

**Pre-finish checks for any AI draft before it is offered.** (1) Read it aloud: if a sentence sounds like a press release, rewrite it. (2) Is the same point repeated in different words: say it once. (3) Does it open with a grand statement about the state of the world: delete it, start on substance.

---

## Lane 2 (the hard boundary): never penalise the student own writing

Hedging, signposting, formal transitions and uniform structure are GOOD academic practice and are natural for neurodivergent and ESL writers (the people Simplifii serves). The lists above must NEVER be run as a detector or a score against the student own Tier 3 writing. Even humans now use these words (their published-writing frequency rose sharply after ChatGPT), so they are a weak signal and never an accusation. Authenticity comes only from the logged provenance, not from scanning the prose. See detector-methods-and-fairness.md.
