import time

from whatsapp_wrapper import WhatsAppAPI
from whatsapp_wrapper.audio_utilities import convert_audio_to_mp3

from configs import DEBUG_CHAT_IDS, GRAPH_API_TOKEN, MOBILE_ID
from openai_wrapper.audio import speech_to_text
from openai_wrapper.chat import correct_text, summarize_text
from openai_wrapper.language import get_intended_language_iso
from translations import DEFAULT_LANGUAGE, check_supported_language, get_localized_message

PROCESSING_REACTION = '👂'
DONE_REACTION = '✅'
FAILED_REACTION = '❌'
META_ERROR_BODY_MAX_CHARS = 500


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


def to_italic(text: str) -> str:
    text_parts = text.split('\n')
    return '\n'.join([f'_{part}_' for part in text_parts])


class MessageProcessor:
    def __init__(self):
        self.wa = WhatsAppAPI(mobile_id=MOBILE_ID, api_token=GRAPH_API_TOKEN, error_handler=raise_with_meta_error)
        self.user_to_language = {}
        self.user_to_transcriptions = {}

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
            try:
                stage = 'download'
                media_file = wa.get_media(media_id)
                stage = 'convert'
                media_file_mp3 = convert_audio_to_mp3(media_file)
                stage = 'transcribe'
                transcription = speech_to_text(media_file_mp3).strip()
            except Exception as e:
                log_audio(recipient_id, message_id, f'failed at {stage}', started, f'{type(e).__name__}: {e}')
                self.send_reaction(recipient_id, message_id, FAILED_REACTION)
                raise
            stage = 'reply'
            if not transcription:
                log_audio(recipient_id, message_id, 'empty transcription', started)
                self.send_reaction(recipient_id, message_id, FAILED_REACTION)
                return {'success': True}
            header = loc('header')
            footer = loc('footer')
            response_msg = f'*{header}*:\n\n{transcription}\n\n{to_italic(footer)}'
        elif message_type == 'text':
            incoming_msg = message['text']['body']
            print(f"[text] {masked(recipient_id)} {short_id(message_id)} received")
            context_id = message.get('context', {}).get('id')
            if context_id:
                try:
                    choice = int(incoming_msg.lower().strip())
                except ValueError:
                    choice = None
                context_msg = self.get_user_transcription(wa_id, context_id)
                if context_msg:
                    if choice == 1:
                        header = loc('correction_header')
                        new_msg = correct_text(context_msg)
                        response_msg = f'*{header}*:\n\n{new_msg}'
                    elif choice == 2:
                        header = loc('summary_header')
                        new_msg = summarize_text(context_msg)
                        response_msg = f'*{header}*:\n\n{new_msg}'
                    elif choice == 3:
                        response_msg = "Sorry, translation is not ready yet."
                    else:
                        response_msg = f"{loc('choice_not_recognized')} {[1, 2, 3]}"
                else:
                    response_msg = loc('context_not_found')
            else:
                iso_code = get_intended_language_iso(incoming_msg)
                success, response_msg = check_supported_language(iso_code, language)
                if success:
                    self.user_to_language[wa_id] = iso_code
        else:
            print(f"[{message_type}] {masked(recipient_id)} {short_id(message_id)} unsupported")
            response_msg = loc('unsupported_content', message_type=message_type)

        if debug:
            response_msg = f"*DEBUG*: {response_msg}"

        try:
            ret = wa.send_text(recipient_id, response_msg, reply_to_message_id=message_id)
        except Exception as e:
            if message_type == 'audio':
                log_audio(recipient_id, message_id, f'failed at {stage}', started, f'{type(e).__name__}: {e}')
                self.send_reaction(recipient_id, message_id, FAILED_REACTION)
            raise
        if message_type == 'audio':
            answer_id = ret['messages'][0]['id']
            self.set_user_transcription(wa_id, answer_id, transcription)
            self.send_reaction(recipient_id, message_id, DONE_REACTION)
            log_audio(recipient_id, message_id, 'ok', started, f'{len(transcription)} chars, reply {short_id(answer_id)}')
        if mark_message_as_read:
            self.mark_as_read(message_id)

        return {'success': True}
