import time

from whatsapp_wrapper import WhatsAppAPI
from whatsapp_wrapper.audio_utilities import convert_audio_to_mp3
from whatsapp_wrapper.message_object import MessageObject

from configs import DEBUG_CHAT_IDS, GRAPH_API_TOKEN, MOBILE_ID
from openai_wrapper.audio import speech_to_text
from openai_wrapper.chat import correct_text, summarize_text, translate_text
from openai_wrapper.language import get_intended_language_iso
from translations import DEFAULT_LANGUAGE, LANGUAGE_NAMES, check_supported_language, get_localized_message

PROCESSING_REACTION = '👂'
DONE_REACTION = '✅'
FAILED_REACTION = '❌'
WORKING_REACTION = '⏳'
META_ERROR_BODY_MAX_CHARS = 500
DEBUG_PREFIX = '*DEBUG*: '

# What the buttons under a transcription do. A button's id is "<action>:<media id>", and a language picked from the
# translation menu is "tr:<iso code>:<media id>", where the media id is WhatsApp's id of the voice note. Transcriptions
# live in memory only, so after a restart a tap finds nothing there: the voice note is then downloaded again from
# WhatsApp and transcribed again, for as long as Meta keeps it.
ACTION_CORRECT = 'fix'
ACTION_SUMMARY = 'sum'
ACTION_TRANSLATE = 'tr'
# People used to answer a transcription with a number; that still works.
NUMERIC_CHOICES = {1: ACTION_CORRECT, 2: ACTION_SUMMARY, 3: ACTION_TRANSLATE}
# Limits Meta puts on interactive messages.
INTERACTIVE_BODY_MAX_CHARS = 1024
TEXT_BODY_MAX_CHARS = 4096
BUTTON_TITLE_MAX_CHARS = 20
LIST_ROW_TITLE_MAX_CHARS = 24


def masked(sender: str) -> str:
    """Last digits of a WhatsApp id, enough to tell senders apart in the logs."""
    return f'…{sender[-4:]}' if sender else '?'


def short_id(message_id: str) -> str:
    return f'…{message_id[-8:]}' if message_id else '?'


def raise_with_meta_error(_wa, response, _data):
    """Error handler for WhatsAppAPI that keeps Meta's answer instead of only the status code."""
    raise Exception(f"Meta answered {response.status_code}: {response.text[:META_ERROR_BODY_MAX_CHARS]}")


def log_audio(sender: str, message_id: str, outcome: str, started: float, detail: str = ''):
    elapsed = time.monotonic() - started
    print(f"[audio] {masked(sender)} {short_id(message_id)} {outcome} {elapsed:.1f}s {detail}".rstrip())


def log_statuses(statuses: list):
    for status in statuses:
        errors = '; '.join(f"{e.get('code')} {e.get('title')}" for e in status.get('errors', []))
        print(f"[status] {status.get('status')} {short_id(status.get('id'))} {errors}".rstrip())


def to_bold(text: str) -> str:
    text_parts = text.split('\n')
    return '\n'.join([f'*{part}*' for part in text_parts])


def split_text(text: str, limit: int = TEXT_BODY_MAX_CHARS) -> list[str]:
    """Cut a text Meta would refuse as too long into pieces, at a line break or a space when there is one."""
    pieces = []
    while len(text) > limit:
        # Only a break in the second half of the piece, so the pieces stay about as long as Meta allows.
        cut = text.rfind('\n', limit // 2, limit + 1)
        if cut == -1:
            cut = text.rfind(' ', limit // 2, limit + 1)
        if cut == -1:
            cut = limit
        pieces.append(text[:cut].rstrip())
        text = text[cut:].lstrip()
    pieces.append(text)
    return pieces


def action_buttons(loc, body: str, key: str) -> dict:
    """Interactive message with one button per thing we can do with a transcription."""
    buttons = [
        (ACTION_CORRECT, loc('btn_correct')),
        (ACTION_SUMMARY, loc('btn_summary')),
        (ACTION_TRANSLATE, loc('btn_translate')),
    ]
    return {
        'type': 'button',
        'body': {'text': body},
        'action': {
            'buttons': [
                {'type': 'reply', 'reply': {'id': f'{action}:{key}', 'title': title[:BUTTON_TITLE_MAX_CHARS]}}
                for action, title in buttons
            ],
        },
    }


def language_menu(loc, key: str) -> dict:
    """Interactive list to pick the language a transcription is translated into."""
    return {
        'type': 'list',
        'body': {'text': loc('translate_prompt')},
        'action': {
            'button': loc('translate_button')[:BUTTON_TITLE_MAX_CHARS],
            'sections': [{
                'title': loc('translate_section')[:LIST_ROW_TITLE_MAX_CHARS],
                'rows': [
                    {'id': f'{ACTION_TRANSLATE}:{iso}:{key}', 'title': native[:LIST_ROW_TITLE_MAX_CHARS]}
                    for iso, (native, _english) in LANGUAGE_NAMES.items()
                ],
            }],
        },
    }


def parse_interactive_reply(message: dict) -> tuple[str, str, str | None] | None:
    """(action, transcription key, target language) of a tapped button or picked list row, None if not ours."""
    interactive = message.get('interactive', {})
    reply = interactive.get(interactive.get('type'), {})
    parts = reply.get('id', '').split(':')
    if len(parts) == 2 and parts[0] in (ACTION_CORRECT, ACTION_SUMMARY, ACTION_TRANSLATE):
        return parts[0], parts[1], None
    if len(parts) == 3 and parts[0] == ACTION_TRANSLATE and parts[1] in LANGUAGE_NAMES:
        return parts[0], parts[2], parts[1]
    return None


class MessageProcessor:
    def __init__(self):
        self.wa = WhatsAppAPI(mobile_id=MOBILE_ID, api_token=GRAPH_API_TOKEN, error_handler=raise_with_meta_error)
        self.user_to_language = {}
        self.user_to_transcriptions = {}
        self.user_to_media = {}

    def set_user_language(self, user_id: str, language: str):
        self.user_to_language[user_id] = language

    def get_user_language(self, user_id: str) -> str:
        return self.user_to_language.get(user_id, DEFAULT_LANGUAGE)

    def set_user_transcription(self, user_id: str, message_id: str, text: str):
        if user_id not in self.user_to_transcriptions:
            self.user_to_transcriptions[user_id] = {}
        self.user_to_transcriptions[user_id][message_id] = text

    def get_user_transcription(self, user_id: str, message_id: str) -> str:
        return self.user_to_transcriptions.get(user_id, {}).get(message_id, '')

    def set_message_media(self, user_id: str, message_id: str, media_id: str):
        self.user_to_media.setdefault(user_id, {})[message_id] = media_id

    def get_message_media(self, user_id: str, message_id: str) -> str:
        """Media id of the voice note one of our messages transcribed, '' if we don't remember it."""
        return self.user_to_media.get(user_id, {}).get(message_id, '')

    def transcribe_media(self, media_id: str, progress: list = None) -> str:
        """Download a voice note from WhatsApp and transcribe it; `progress` gets the stage being worked on."""
        progress = [] if progress is None else progress
        progress.append('download')
        media_file = self.wa.get_media(media_id)
        progress.append('convert')
        media_file_mp3 = convert_audio_to_mp3(media_file)
        progress.append('transcribe')
        return speech_to_text(media_file_mp3).strip()

    def find_transcription(self, recipient_id: str, wa_id: str, key: str) -> str:
        """The transcription a button points at, transcribed again when a restart wiped it from memory."""
        text = self.get_user_transcription(wa_id, key)
        if text or not key.isdigit():
            return text
        started = time.monotonic()
        try:
            text = self.transcribe_media(key)
        except Exception as e:
            print(f"[retranscribe] {masked(recipient_id)} failed {time.monotonic() - started:.1f}s "
                  f"{type(e).__name__}: {e}")
            return ''
        print(f"[retranscribe] {masked(recipient_id)} ok {time.monotonic() - started:.1f}s {len(text)} chars")
        if text:
            self.set_user_transcription(wa_id, key, text)
        return text

    def send_reaction(self, recipient_id: str, message_id: str, emoji: str):
        try:
            self.wa.send_reaction(recipient_id, message_id, emoji, save_to_db=False)
        except Exception as e:
            print(f"Failed to send reaction {emoji} to message {message_id}: {e}")

    def mark_as_read(self, message_id: str):
        try:
            self.wa.mark_as_read(message_id)
        except Exception as e:
            print(f"Failed to mark message {message_id} as read: {e}")

    def send_interactive(self, recipient_id: str, interactive: dict, reply_to_message_id: str = None) -> dict:
        payload = MessageObject(recipient_id, reply_to_message_id=reply_to_message_id).base_data
        payload['type'] = 'interactive'
        payload['interactive'] = interactive
        return self.wa._send_message(payload, save_to_db=False)

    def send_reply(self, recipient_id: str, message_id: str, parts: list, debug: bool = False) -> list[str]:
        """Send each part (text, or an interactive dict) as a reply to the previous one; return the sent ids.

        A text longer than Meta allows goes out in several messages.
        """
        if debug and parts:
            if isinstance(parts[0], str):
                parts[0] = f'{DEBUG_PREFIX}{parts[0]}'
            else:
                parts[0]['body']['text'] = f"{DEBUG_PREFIX}{parts[0]['body']['text']}"
        sent_ids = []
        reply_to = message_id
        for part in parts:
            for piece in split_text(part) if isinstance(part, str) else [part]:
                if isinstance(piece, str):
                    ret = self.wa.send_text(recipient_id, piece, reply_to_message_id=reply_to)
                else:
                    ret = self.send_interactive(recipient_id, piece, reply_to_message_id=reply_to)
                reply_to = ret['messages'][0]['id']
                sent_ids.append(reply_to)
        return sent_ids

    def transcription_reply(self, loc, transcription: str, key: str, debug: bool = False) -> list:
        """The transcription with the action buttons under it, in one message when Meta lets us."""
        text = f"*{loc('header')}*:\n\n{transcription}"
        prefix_chars = len(DEBUG_PREFIX) if debug else 0
        if prefix_chars + len(text) <= INTERACTIVE_BODY_MAX_CHARS:
            return [action_buttons(loc, text, key)]
        return [text, action_buttons(loc, loc('actions_prompt'), key)]

    def run_action(self, loc, action: str, text: str, key: str, target: str = None) -> list:
        """What to answer when someone asks to correct, summarize or translate a transcription."""
        if action == ACTION_CORRECT:
            return [f"*{loc('correction_header')}*:\n\n{correct_text(text)}"]
        if action == ACTION_SUMMARY:
            return [f"*{loc('summary_header')}*:\n\n{summarize_text(text)}"]
        if target is None:
            return [language_menu(loc, key)]
        native, english = LANGUAGE_NAMES[target]
        return [f"*{loc('translation_header')}* ({native}):\n\n{translate_text(text, english)}"]

    def answer_action(self, loc, recipient_id: str, message_id: str, wa_id: str, action: str, key: str,
                      target: str = None) -> list:
        calls_model = action != ACTION_TRANSLATE or target is not None
        label = f'{action}:{target}' if target else action
        remembered = bool(self.get_user_transcription(wa_id, key))
        if calls_model or not remembered:
            self.send_reaction(recipient_id, message_id, WORKING_REACTION)
        text = self.find_transcription(recipient_id, wa_id, key)
        if not text:
            self.send_reaction(recipient_id, message_id, FAILED_REACTION)
            return [loc('context_not_found')]
        started = time.monotonic()
        try:
            parts = self.run_action(loc, action, text, key, target)
        except Exception as e:
            print(f"[action] {masked(recipient_id)} {label} failed {time.monotonic() - started:.1f}s "
                  f"{type(e).__name__}: {e}")
            self.send_reaction(recipient_id, message_id, FAILED_REACTION)
            return [loc('action_failed')]
        if calls_model or not remembered:
            self.send_reaction(recipient_id, message_id, DONE_REACTION)
        if calls_model:
            print(f"[action] {masked(recipient_id)} {label} ok {time.monotonic() - started:.1f}s")
        return parts

    def process_webhook_post_request(self, data, mark_message_as_read: bool = True, debug: bool = False) -> dict:
        wa = self.wa
        entry = data['entry'][0]
        changes = entry['changes']
        last_change = changes[0]['value']
        phone_number_id = last_change.get('metadata', {}).get('phone_number_id')
        if phone_number_id != MOBILE_ID:
            print("Ignoring webhook not addressed to this bot's phone number")
            return {'success': True}
        if 'messages' not in last_change:
            log_statuses(last_change.get('statuses', []))
            return {'success': True}
        message = last_change['messages'][0]
        wa_id = last_change['contacts'][0]['wa_id']
        language = self.get_user_language(wa_id)
        loc = lambda key, **kwargs: get_localized_message(language, key, **kwargs)
        message_type = message['type']
        recipient_id = message['from']
        if debug and recipient_id not in DEBUG_CHAT_IDS:
            print(f"User {masked(recipient_id)} is not in debug chat ids. Ignoring message.")
            return {'success': True}
        banned_users = wa.banned_users
        if recipient_id in banned_users:
            print(f"User {masked(recipient_id)} is banned. Ignoring message.")
            return {'success': True}
        message_id = message['id']
        if mark_message_as_read:
            self.mark_as_read(message_id)
        transcription = None
        started = time.monotonic()
        stage = 'reply'
        if message_type == 'audio':
            log_audio(recipient_id, message_id, 'received', started)
            self.send_reaction(recipient_id, message_id, PROCESSING_REACTION)
            media_id = message['audio']['id']
            progress = []
            try:
                transcription = self.transcribe_media(media_id, progress)
            except Exception as e:
                stage = progress[-1] if progress else 'download'
                log_audio(recipient_id, message_id, f'failed at {stage}', started, f'{type(e).__name__}: {e}')
                self.send_reaction(recipient_id, message_id, FAILED_REACTION)
                raise
            stage = 'reply'
            if not transcription:
                log_audio(recipient_id, message_id, 'empty transcription', started)
                self.send_reaction(recipient_id, message_id, FAILED_REACTION)
                return {'success': True}
            # Stored under the voice note's media id before sending, so the buttons can point at it.
            self.set_user_transcription(wa_id, media_id, transcription)
            parts = self.transcription_reply(loc, transcription, media_id, debug=debug)
        elif message_type == 'interactive':
            print(f"[interactive] {masked(recipient_id)} {short_id(message_id)} received")
            parsed = parse_interactive_reply(message)
            if parsed:
                action, key, target = parsed
                parts = self.answer_action(loc, recipient_id, message_id, wa_id, action, key, target)
            else:
                parts = [loc('context_not_found')]
        elif message_type == 'text':
            incoming_msg = message['text']['body']
            print(f"[text] {masked(recipient_id)} {short_id(message_id)} received")
            context_id = message.get('context', {}).get('id')
            if context_id:
                try:
                    choice = int(incoming_msg.lower().strip())
                except ValueError:
                    choice = None
                key = self.get_message_media(wa_id, context_id)
                if not key:
                    parts = [loc('context_not_found')]
                elif choice in NUMERIC_CHOICES:
                    parts = self.answer_action(loc, recipient_id, message_id, wa_id, NUMERIC_CHOICES[choice], key)
                else:
                    parts = [action_buttons(loc, loc('actions_prompt'), key)]
            else:
                iso_code = get_intended_language_iso(incoming_msg)
                success, response_msg = check_supported_language(iso_code, language)
                if success:
                    self.user_to_language[wa_id] = iso_code
                parts = [response_msg]
        else:
            print(f"[{message_type}] {masked(recipient_id)} {short_id(message_id)} unsupported")
            parts = [loc('unsupported_content', message_type=message_type)]

        try:
            sent_ids = self.send_reply(recipient_id, message_id, parts, debug=debug)
        except Exception as e:
            if message_type == 'audio':
                log_audio(recipient_id, message_id, f'failed at {stage}', started, f'{type(e).__name__}: {e}')
                self.send_reaction(recipient_id, message_id, FAILED_REACTION)
            raise
        if message_type == 'audio':
            # Quoting any of our messages with a number still finds the transcription.
            for sent_id in sent_ids:
                self.set_message_media(wa_id, sent_id, media_id)
            self.send_reaction(recipient_id, message_id, DONE_REACTION)
            log_audio(recipient_id, message_id, 'ok', started,
                      f'{len(transcription)} chars, reply {short_id(sent_ids[-1])}')
        if mark_message_as_read:
            self.mark_as_read(message_id)

        return {'success': True}
