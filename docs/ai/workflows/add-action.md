# Add a reply button or change what one does

The buttons under a transcription are `ACTIONS` in
[`message_processor.py`](../../../message_processor.py), in display order. WhatsApp allows at most
three reply buttons, so a fourth action needs a different design (a list): ask first.

To change what an action does, change its function in
[`openai_wrapper/chat.py`](../../../openai_wrapper/chat.py) and stop there.

To add or replace one (PR #13 added the buttons, PR #10 the translation menu):

1. Write the OpenAI function in `openai_wrapper/chat.py` on top of `simple_query`, with a prompt that
   keeps the text's language and asks for the result only.
2. Route it in `run_action` ([`message_processor.py:99`](../../../message_processor.py)).
3. Add `<action>_button` and `<action>_header` to every language in `translations.py`
   ([add-message-or-language.md](./add-message-or-language.md)).
4. Add the name to `ACTIONS`. Ids stay `'<action>:<media id>'`; if the action needs a parameter, add
   it the way translate does (`parse_reply_id` and a menu), keeping old ids readable since buttons
   already sent keep working.
5. The typed replies `1`, `2`, `3` follow `ACTIONS` order through `action_from_typed_choice`: a
   reorder changes what they pick.
6. Check by hand on the test route ([`testing.md`](../testing.md)): tap the button on a fresh
   transcription and on one sent before a restart (the retranscribe path).
7. Update [`reusability.md`](../reusability.md) and, if the flow changed, [`patterns.md`](../patterns.md).
