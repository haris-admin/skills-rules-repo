# Honcho Bridge Limitations

**Last verified:** June 2, 2026

## Current State

The Pluto↔Honcho bridge is **outbound-only**. The `pluto_honcho_bridge_daily` cron job (6:00 AM AEST) pushes Pluto's research outputs (JSON, MD) to Honcho as `[pluto]` peer messages. This direction works reliably.

## Inbound Gap

There is **no automated mechanism** for Haris or Gumby to push documents TO Pluto via Honcho. When the user says "there's a document for you from the honcho push," Pluto cannot retrieve it from Honcho peers or Honcho messages.

### Known Limitations
- `honcho_context` searches peer conversation history — useful for context, not document pickup
- `honcho_search` returns fact observations, not file attachments
- No Honcho MCP tool for file transfer or document retrieval
- The bridge state file (`~/.hermes/research_outputs/.honcho_bridge_state.json`) is write-only (Pluto → Honcho push tracking)

## Workaround

If the user mentions a "honcho push document":
1. Ask for the direct file path (Desktop, Downloads, mempalace-inputs/)
2. Check standard drop locations:
   - `/mnt/c/Users/habib/Desktop/`
   - `/mnt/c/Users/habib/Downloads/`
   - `/home/habib/.hermes/mempalace-inputs/`
3. Do NOT spend cycles searching Honcho peers — the bridge doesn't support inbound
4. Consider suggesting the user drop files directly into `~/.hermes/mempalace-inputs/` as an alternative channel

## Future: Two-Way Bridge

If Haris wants true two-way document sharing, options include:
- A shared watch directory (e.g., `~/.hermes/bridge-inbox/`) monitored by a cron job
- Extending the Honcho bridge to support inbound file attachments
- Using Gumby's existing handoff mechanism (`gumby-brief-input.md`) in reverse
