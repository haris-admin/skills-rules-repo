# OpenRouter LLM Cost Comparison — June 2026

Pricing in USD per 1 million tokens. Retrieved June 1, 2026 from OpenRouter API.

## DeepSeek Models

| Model | Prompt/1M | Completion/1M | Context | Best For |
|-------|-----------|---------------|---------|----------|
| **v4 Flash** | $0.098 | $0.197 | 1M | Cron research (4.4x cheaper) |
| v3.2 | $0.229 | $0.343 | 131K | Budget interactive |
| v3.2 Exp | $0.270 | $0.410 | 164K | Experimental |
| v3.1 Chat | $0.210 | $0.790 | 164K | Legacy |
| v4 Pro | $0.435 | $0.870 | 1M | Interactive sessions (current) |
| R1 | $0.700 | $2.500 | 164K | Reasoning-heavy |
| R1 Distill Qwen 32B | $0.290 | $0.290 | 128K | Budget reasoning |
| R1 0528 | $0.500 | $2.150 | 164K | Latest reasoning |

## MiniMax Models

| Model | Prompt/1M | Completion/1M | Context | vs v4 Flash |
|-------|-----------|---------------|---------|-------------|
| M3 | $0.300 | $1.200 | 1M | +206% prompt, +509% completion |
| M2.7 | $0.260 | $1.200 | 205K | Higher cost |
| M2.5 | $0.150 | $1.150 | 205K | +53% prompt, +484% completion |
| M2.1 | $0.290 | $0.950 | 205K | Higher cost |
| M2 | $0.255 | $1.000 | 205K | Higher cost |
| M1 | $0.400 | $2.200 | 1M | Highest cost |
| MiniMax-01 | $0.200 | $1.100 | 1M | Higher cost |

## Audio Models (OpenRouter)

| Model | Prompt/1M | Completion/1M | Use |
|-------|-----------|---------------|-----|
| GPT Audio Mini | $0.600 | $2.400 | Voice transcription (~$0.0003/msg) |
| GPT Audio | $2.500 | $10.000 | Full audio processing |

## Key Decisions (June 1, 2026)

- **Cron research jobs → v4 Flash** (`deepseek/deepseek-v4-flash`): 4.4x cheaper, same 1M context
- **Interactive sessions → v4 Pro** (`deepseek/deepseek-v4-pro`): Stronger reasoning, kept for complex tasks
- **MiniMax M3 is NOT cheaper** than v4 Flash on any metric. On completion (where most cost lives), M3 is 6.1x more expensive than Flash.
- **OpenRouter does NOT proxy TTS or Whisper.** Use direct OpenAI API for those.
