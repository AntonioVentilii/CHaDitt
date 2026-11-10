# Add or reword a message, or add a language

## A message

1. Look for an existing key in `localized_messages` ([`translations.py`](../../../translations.py))
   that already says it; reuse it if so.
2. Add the key to **every** language block, in the same position. A key missing from one language
   makes `get_localized_message` raise `ValueError` for every sender in that language.
3. Placeholders use `str.format` names (`{language}`, `{message_type}`); pass them as keyword
   arguments to `get_localized_message`.
4. A button or list title must fit WhatsApp's limits (20 characters for a button, 24 for a list row):
   count every language.
5. Use it from `MessageProcessor` through `get_localized_message(language, key)`, never a literal.
6. Add the key to the list in [`reusability.md`](../reusability.md).

## A language

1. Add a block to `localized_messages` with every key, `language_name` in English (it goes into the
   translation prompt).
2. Add its native label with a flag to `LANGUAGE_LABELS`. The translation menu is a WhatsApp list:
   at most 10 rows.
3. Add the calling codes where it is the one main supported language to
   `COUNTRY_CALLING_CODE_LANGUAGES`, and leave out codes shared with another supported language
   (the comment above the dict says why).
4. Check that `get_intended_language_iso` returns its ISO 639-1 code for a request written in it.
5. Update the language count in [`AGENTS.md`](../../../AGENTS.md) and the root `README.md` if they name it.
