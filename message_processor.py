import time

from whatsapp_wrapper import WhatsAppAPI
from whatsapp_wrapper.audio_utilities import convert_audio_to_mp3
from whatsapp_wrapper.message_object import MessageObject

from configs import DEBUG_CHAT_IDS, GRAPH_API_TOKEN, MOBILE_ID
from openai_wrapper.audio import speech_to_text
from openai_wrapper.chat import correct_text, summarize_text, translate_text
from openai_wrapper.language import get_intended_language_iso
from translations import DEFAULT_LANGUAGE, check_supported_language, get_localized_message, language_for_wa_id

PROCESSING_REACTION = '👂'
DONE_REACTION = '✅'
FAILED_REACTION = '❌'
META_ERROR_BODY_MAX_CHARS = 500
# WhatsApp allows at most 1024 characters in the body of a message with reply buttons.
BUTTONS_BODY_MAX_CHARS = 1024
FALLBACK_TRANSLATION_LANGUAGE = 'en'

# What a transcription can be turned into, in the order of its buttons. The button id is the action, its title
# is the '<action>_button' message and the answer starts with the '<action>_header' message.
# A typed reply of 1, 2 or 3 to a transcription picks the same action.
ACTIONS = ('correct', 'summarize', 'translate')


def masked(sender: str) -> str:
    """Last digits of a WhatsApp id, enough to tell senders apart in the logs."""
    return f'…{sender[-4:]}' if sender else '?'


def short_id(message_id: str) -> str:
    return f'…{message_id[-8:]}' if message_id else '?'


def raise_with_meta_error(_wa, response, _data):
    """Error handler for WhatsAppAPI that keeps Meta's answer instead of only the status code."""
    raise Exception(f"Meta answered {response.status_code}: {response.text[:META_ERROR_BODY_MAX_CHARS]}")


def log_outcome(kind: str, sender: str, message_id: str, outcome: str, started: float, detail: str = ''):
    elapsed = time.monotonic() - started
    print(f"[{kind}] {masked(sender)} {short_id(message_id)} {outcome} {elapsed:.1f}s {detail}".rstrip())


def log_statuses(statuses: list):
    for status in statuses:
        errors = '; '.join(f"{e.get('code')} {e.get('title')}" for e in status.get('errors', []))
        print(f"[status] {status.get('status')} {short_id(status.get('id'))} {errors}".rstrip())


def describe(e: Exception) -> str:
    return f'{type(e).__name__}: {e}'


def translation_languages(language: str) -> tuple[str, str]:
    """The language to translate into and the one to use when the text is already in it."""
    fallback = DEFAULT_LANGUAGE if language != DEFAULT_LANGUAGE else FALLBACK_TRANSLATION_LANGUAGE
    return (get_localized_message(language, 'language_name'),
            get_localized_message(fallback, 'language_name'))


def run_action(action: str, text: str, language: str) -> str:
    if action == 'correct':
        return correct_text(text)
    if action == 'summarize':
        return summarize_text(text)
    if action == 'translate':
        return translate_text(text, *translation_languages(language))
    raise ValueError(f"Unknown action '{action}'")


def action_from_typed_choice(text: str) -> str | None:
    choice = text.strip()
    if choice.isdigit() and 1 <= int(choice) <= len(ACTIONS):
        return ACTIONS[int(choice) - 1]
    return None


class MessageProcessor:
    def __init__(self):
        self.wa = WhatsAppAPI(mobile_id=MOBILE_ID, api_token=GRAPH_API_TOKEN, error_handler=raise_with_meta_error)
        self.user_to_language = {}
        self.user_to_transcriptions = {}

    def set_user_language(self, user_id: str, language: str):
        self.user_to_language[user_id] = language

    def get_user_language(self, user_id: str) -> str:
        return self.user_to_language.get(user_id) or language_for_wa_id(user_id)

    def set_user_transcription(self, user_id: str, message_id: str, text: str):
        if user_id not in self.user_to_transcriptions:
            self.user_to_transcriptions[user_id] = {}
        self.user_to_transcriptions[user_id][message_id] = text

    def get_user_transcription(self, user_id: str, message_id: str) -> str:
        return self.user_to_transcriptions.get(user_id, {}).get(message_id, '')

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

    def send_text(self, to: str, text: str, reply_to: str) -> str:
        # Not saved to the wrapper's database: without one it would warn with the whole message in the logs.
        ret = self.wa.send_text(to, text, reply_to_message_id=reply_to, save_to_db=False)
        return ret['messages'][0]['id']

    def send_buttons(self, to: str, body: str, reply_to: str, language: str) -> str:
        """Sends body with one reply button per action and returns the id of the message."""
        data = MessageObject(to, reply_to_message_id=reply_to).base_data
        data['type'] = 'interactive'
        data['interactive'] = {
            'type': 'button',
            'body': {'text': body},
            'action': {'buttons': [
                {'type': 'reply', 'reply': {'id': action, 'title': get_localized_message(language, f'{action}_button')}}
                for action in ACTIONS
            ]},
        }
        ret = self.wa._send_message(data, save_to_db=False)
        return ret['messages'][0]['id']

    def send_transcription(self, to: str, transcription: str, reply_to: str, language: str) -> list[str]:
        """Sends the transcription with the action buttons and returns the ids a reply can point to."""
        header = get_localized_message(language, 'header')
        text = f'*{header}*\n\n{transcription}'
        if len(text) <= BUTTONS_BODY_MAX_CHARS:
            return [self.send_buttons(to, text, reply_to, language)]
        text_id = self.send_text(to, text, reply_to)
        buttons_id = self.send_buttons(to, get_localized_message(language, 'actions_prompt'), text_id, language)
        return [text_id, buttons_id]

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
        message_type = message['type']
        recipient_id = message['from']
        if debug and recipient_id not in DEBUG_CHAT_IDS:
            print(f"User {masked(recipient_id)} is not in debug chat ids. Ignoring message.")
            return {'success': True}
        if recipient_id in wa.banned_users:
            print(f"User {masked(recipient_id)} is banned. Ignoring message.")
            return {'success': True}
        message_id = message['id']
        if mark_message_as_read:
            self.mark_as_read(message_id)

        if message_type == 'audio':
            self.process_audio(message, wa_id, debug)
        elif message_type == 'interactive' and message['interactive'].get('type') == 'button_reply':
            action = message['interactive']['button_reply']['id']
            self.process_action(message, wa_id, action, debug)
        elif message_type == 'text':
            self.process_text(message, wa_id, debug)
        else:
            print(f"[{message_type}] {masked(recipient_id)} {short_id(message_id)} unsupported")
            language = self.get_user_language(wa_id)
            reply = get_localized_message(language, 'unsupported_content', message_type=message_type)
            self.send_text(recipient_id, self.debug_prefix(reply, debug), message_id)
        return {'success': True}

    @staticmethod
    def debug_prefix(text: str, debug: bool) -> str:
        return f"*DEBUG*: {text}" if debug else text

    def process_audio(self, message: dict, wa_id: str, debug: bool):
        recipient_id = message['from']
        message_id = message['id']
        language = self.get_user_language(wa_id)
        started = time.monotonic()
        stage = 'download'
        log_outcome('audio', recipient_id, message_id, 'received', started)
        self.send_reaction(recipient_id, message_id, PROCESSING_REACTION)
        try:
            media_file = self.wa.get_media(message['audio']['id'])
            stage = 'convert'
            media_file_mp3 = convert_audio_to_mp3(media_file)
            stage = 'transcribe'
            transcription = speech_to_text(media_file_mp3).strip()
            if not transcription:
                log_outcome('audio', recipient_id, message_id, 'empty transcription', started)
                self.send_reaction(recipient_id, message_id, FAILED_REACTION)
                return
            stage = 'reply'
            answer_ids = self.send_transcription(recipient_id, self.debug_prefix(transcription, debug), message_id,
                                                 language)
        except Exception as e:
            log_outcome('audio', recipient_id, message_id, f'failed at {stage}', started, describe(e))
            self.send_reaction(recipient_id, message_id, FAILED_REACTION)
            raise
        for answer_id in answer_ids:
            self.set_user_transcription(wa_id, answer_id, transcription)
        self.send_reaction(recipient_id, message_id, DONE_REACTION)
        log_outcome('audio', recipient_id, message_id, 'ok', started,
                    f'{len(transcription)} chars, reply {short_id(answer_ids[-1])}')

    def process_action(self, message: dict, wa_id: str, action: str, debug: bool):
        """Runs a button's action on the transcription the button belongs to and replies to that transcription."""
        recipient_id = message['from']
        message_id = message['id']
        language = self.get_user_language(wa_id)
        started = time.monotonic()
        context_id = message.get('context', {}).get('id')
        transcription = self.get_user_transcription(wa_id, context_id)
        if not transcription:
            log_outcome(action, recipient_id, message_id, 'context not found', started)
            reply = get_localized_message(language, 'context_not_found')
            self.send_text(recipient_id, self.debug_prefix(reply, debug), message_id)
            return
        try:
            result = run_action(action, transcription, language)
            header = get_localized_message(language, f'{action}_header')
            self.send_text(recipient_id, self.debug_prefix(f'*{header}*\n\n{result}', debug), context_id)
        except Exception as e:
            log_outcome(action, recipient_id, message_id, 'failed', started, describe(e))
            self.send_failure(recipient_id, message_id, language)
            return
        log_outcome(action, recipient_id, message_id, 'ok', started, f'{len(result)} chars')

    def process_text(self, message: dict, wa_id: str, debug: bool):
        recipient_id = message['from']
        message_id = message['id']
        language = self.get_user_language(wa_id)
        started = time.monotonic()
        incoming_msg = message['text']['body']
        log_outcome('text', recipient_id, message_id, 'received', started)
        if message.get('context', {}).get('id'):
            action = action_from_typed_choice(incoming_msg)
            if action:
                self.process_action(message, wa_id, action, debug)
                return
            reply = get_localized_message(language, 'choice_not_recognized')
            self.send_text(recipient_id, self.debug_prefix(reply, debug), message_id)
            return
        try:
            iso_code = get_intended_language_iso(incoming_msg)
        except Exception as e:
            log_outcome('text', recipient_id, message_id, 'failed at language', started, describe(e))
            self.send_failure(recipient_id, message_id, language)
            return
        success, reply = check_supported_language(iso_code, language)
        if success:
            self.set_user_language(wa_id, iso_code)
        log_outcome('text', recipient_id, message_id, f'language {iso_code}', started)
        self.send_text(recipient_id, self.debug_prefix(reply, debug), message_id)

    def send_failure(self, recipient_id: str, message_id: str, language: str):
        try:
            self.send_text(recipient_id, get_localized_message(language, 'action_failed'), message_id)
        except Exception as e:
            print(f"Failed to tell {masked(recipient_id)} that something went wrong: {e}")
