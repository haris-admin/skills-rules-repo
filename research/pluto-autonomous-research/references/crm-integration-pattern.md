# AU Real Estate CRM Integration — Competitive Intelligence

## Context

July 3, 2026. AML Hive targets AU real estate agencies for AML/CTF compliance (Tranche 2). Integrating directly into the CRMs agents already use is a distribution moat — embedded compliance is stickier than a separate login.

## Key Competitive Signal — Reapit Verify

**Reapit launched AML/CTF compliance built into their CRM** (June 2026). This is a direct competitive threat: agents don't need a separate AML Hive login if Reapit handles compliance inside their existing workflow. Reapit is UK-based with strong AU presence. This validates the CRM-integration strategy but raises the urgency — first-mover advantage in the CRM-integration space matters.

## Top 10 AU Real Estate CRMs (Integration Targets)

| Rank | CRM | Parent/Owner | AU Market Position | API Status | Integration Priority |
|------|-----|-------------|-------------------|-----------|---------------------|
| 1 | **Rex Software (PropertyTree)** | Rex Software | #1 AU real estate CRM. Cloud-based, built for AU agents. Just launched Rex AI (May 2026). | REST API. Strong partner ecosystem. | **CRITICAL** — highest market share |
| 2 | **MRI Software (Console Cloud)** | MRI Software (US PE-backed) | Widely used by AU agencies. REA Group integrates for data-enriched leads. | REST API. Open for integrations. | **HIGH** — REA Group already integrating |
| 3 | **Reapit** | Reapit (UK) | Strong AU presence. JUST launched Verify with AML/CTF (direct competitive threat). | REST API. Partner programme. | **HIGH** — competitive response needed |
| 4 | **PropertyMe** | PropertyMe (AU, EQT-backed) | Cloud property management. Acquired Phoenix Software (Oct 2025) to expand into CRM. EQT investing. | REST API. | **HIGH** — growing, well-funded |
| 5 | **Aspire Software** | Aspire (AU) | AU real estate CRM with property management. Mid-market. | API available. | **MEDIUM** |
| 6 | **Agency Plus** | Agency Plus (AU) | Full agency management suite (CRM + accounting + trust). Widely used. | API via partnership. | **MEDIUM** |
| 7 | **Rocket Agent** | Rocket Agent (AU) | Independent agency CRM. Popular with smaller/independent agencies. | REST API. | **MEDIUM** — good for SMB segment |
| 8 | **CoreLogic RP Data CRM** | CoreLogic (US) | Data-integrated CRM. CoreLogic controls property data (valuation, title). | Limited API. Data licensing constraints. | **LOW** — hard to integrate |
| 9 | **rest Professional (Rockend)** | Rockend/Console (AU) | Property management + CRM. Used by specialist PMs. | API available. | **LOW** — property mgmt focused |
| 10 | **Salesforce Real Estate Cloud** | Salesforce (US) | Used by enterprise franchise groups (Ray White, LJ Hooker, etc.). | Strong APIs. | **LOW** — enterprise only, expensive |

## Integration Approach

### Phase 1: Partner (no-code / lightweight)
- **Zapier/Make integration** — fastest path. Agent can connect AML Hive to any CRM that supports webhooks.
- **Browser extension** — scrape/know agent CRM screen, inject compliance status. Fragile but zero CRM-side dev.

### Phase 2: API (REST)
- **Direct REST API integration** with top 3 CRMs (Rex, MRI, Reapit). Each has partner programmes.
- **Webhook-based CDD triggers** — when CRM creates a new client, push to AML Hive for screening.
- **Status widget** — embed compliance status (PASS/FAIL/PENDING) inside CRM contact record.

### Phase 3: Embedded (deepest)
- **White-label widget** — AML Hive compliance panel rendered inside CRM UI (iFrame or SDK).
- **One-click screening** — no context switch for the agent.
- **Automated AUSTRAC reporting** — CRM data flows through AML Hive → SMR submission.

## Companies to Approach

| CRM | Contact Route | Notes |
|-----|-------------|-------|
| Rex Software | Developer partner programme | Tom Ainsworth is CEO. Knows AI/automation (just launched Rex AI). |
| MRI Software | Existing partner network | REA Group already integrates — use similar approach. |
| Reapit | Competitive — approach differently | They just built AML in-house. Partner or compete. |
| PropertyMe | EQT-backed, acquisition mode | Recently acquired Phoenix — may be open to more integrations. |
