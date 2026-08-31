---
name: structured-outputs-first
description: Any AI endpoint that must return JSON uses Anthropic tool use (structured outputs), never text generation plus regex parsing. ALWAYS load when designing or reviewing any API endpoint that calls an LLM and parses its response, when CC-T reports "JSON parse failed", "could not be parsed", fence-stripping, markdown wrapping, control characters, or truncated responses, or when anyone proposes a JSON repair, sanitise, or cleanup layer. Also load for any new Simplifii AI feature (scaffolds, decodes, classification, AURA structured replies).
---

# Structured Outputs First

Established 11 Jun 2026 after three patch layers (fence-stripping, control-char sanitising, aggressive cleanup) failed on both simplify-brief and decode-rubric in production on tester eve. The text-then-parse pattern is banned for JSON endpoints.

## The rule

Every endpoint where the model's output is parsed as JSON uses tool use:

```js
tools: [{
  name: 'emit_result',
  description: 'Return the structured result as valid JSON.',
  input_schema: { /* derived from CONSUMERS, see below */ },
}],
tool_choice: { type: 'tool', name: 'emit_result' },
stream: true,
```

Streaming accumulates `input_json_delta` events (`evt.delta.partial_json`), not `content_block_delta.text`. One plain `JSON.parse` at the end. No fence-stripping, no regex extraction, no sanitising, no repair: all dead code under tool use, delete on sight.

## The two guards that travel with it

Tool use guarantees valid JSON only when generation FINISHES. Two guards are mandatory in every converted endpoint:

1. **stop_reason guard.** Capture `stop_reason` from `message_delta` events. If it is `max_tokens`, skip JSON.parse entirely, log `[endpoint] TRUNCATED at <n> tokens`, return the honest failure state. Truncated tool input is broken JSON; parsing it is wasted, repairing it is dangerous.
2. **Token headroom.** Set max_tokens from the largest real document in the golden set, not from optimism. A ceiling that truncates real inputs makes tool use look broken when the format was never the problem. When a tap fails post-conversion, check output_tokens vs ceiling FIRST.

## Schema = consumers

The input_schema is derived only from the fields the frontend actually reads (grep the consumers: normalisers, panels, renderers). Print field-to-consumer file:line. Fields invented from the prompt text are contract drift; fields the consumer reads but the schema omits break rendering with technically valid JSON.

## Why repair layers are banned, not just discouraged

Quote-counting and bracket-closing on truncated JSON produces VALID JSON with silently amputated content. A student receives a plan missing its final weeks with no error: a B-012-class trust failure dressed as success. An honest "Try again" beats a silently corrupted scaffold every time. If anyone (including CC-T, including a future Claude) proposes a repair layer, the correct response is to stop the commit and convert to tool use.

## Failure diagnosis order (post-conversion)

If a tool-use endpoint still fails:
1. stop_reason: if max_tokens, the OUTPUT is too large, not the format. Fix = reduce demanded depth or two-pass (summary first, detail on demand). Not a format problem, do not touch the parsing.
2. Schema rejection (400 from API): schema too strict for what the prompt demands. Loosen nested object schemas to `{ type: 'object' }` and validate downstream.
3. Anything else: read the Railway log line before forming a hypothesis. Step 0 always.
