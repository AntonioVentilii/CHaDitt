# The OpenAI models the bot uses, in one place: when OpenAI retires one, change it here.
# Check https://platform.openai.com/docs/deprecations before picking one.
# As of November 2026: gpt-transcribe costs about $0.0045 per audio minute (whisper-1 was $0.006 and is retired in
# February 2027); gpt-6-luna costs $0.10 per million input tokens and $0.50 per million output tokens
# (gpt-5.4-nano, twice the price, is retired in April 2027).
TRANSCRIPTION_MODEL = 'gpt-transcribe'
CHAT_MODEL = 'gpt-6-luna'
# Correcting, summarizing and translating a voice note needs no reasoning: 'none' keeps answers fast and cheap.
CHAT_REASONING_EFFORT = 'none'
