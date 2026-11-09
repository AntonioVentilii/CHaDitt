# The OpenAI models the bot uses, in one place: when OpenAI retires one, change it here.
# Prices as of November 2026: gpt-transcribe about $0.0045 per audio minute (whisper-1 was $0.006 and is
# retired in February 2027); gpt-5.4-nano $0.20 per million input tokens and $1.25 per million output tokens.
TRANSCRIPTION_MODEL = 'gpt-transcribe'
CHAT_MODEL = 'gpt-5.4-nano'
# Correcting, summarizing and translating a voice note needs no reasoning: 'none' keeps answers fast and cheap.
CHAT_REASONING_EFFORT = 'none'
