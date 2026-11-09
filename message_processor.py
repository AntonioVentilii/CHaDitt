import time

from whatsapp_wrapper import WhatsAppAPI
from whatsapp_wrapper.audio_utilities import convert_audio_to_mp3
from whatsapp_wrapper.message_object import MessageObject

from configs import DEBUG_CHAT_IDS, GRAPH_API_TOKEN, MOBILE_ID
from openai_wrapper.audio import speech_to_text
from openai_wrapper.chat import correct_text, summarize_text, translate_text
from openai_wrapper.language import get_intended_language_iso
from translations import (DEFAULT_LANGUAGE, LANGUAGE_LABELS, check_supported_language, get_localized_message,
                          language_for_wa_id)

PROCESSING_REACTION = '👂'
# On a tapped button or a picked language while the model works on it.
WORKING_REACTION = '⏳'
DONE_REACTION = '✅'
FAILED_REACTION = '❌'
META_ERROR_BODY_MAX_CHARS = 500
# WhatsApp allows at most 1024 characters in the body of a message with reply buttons.
BUTTONS_BODY_MAX_CHARS = 1024
# And at most 20 characters in a button's title, 24 in a list row's.
BUTTON_TITLE_MAX_CHARS = 20
LIST_ROW_TITLE_MAX_CHARS = 24
# And at most 4096 in a text message: a longer one goes out in several.
TEXT_BODY_MAX_CHARS = 4096
FALLBACK_TRANSLATION_LANGUAGE = 'en'

# What a transcription can be turned into, in the order of its buttons. The button id is '<action>:<media id>',
# with the WhatsApp id of the voice note, its title is the '<action>_button' message and the answer starts with the
# '<action>_header' message. A typed reply of 1, 2 or 3 to a transcription picks the same action.
# Translate opens a menu of languages; a row's id is 'translate:<iso code>:<media id>'.
# Transcriptions live in memory only: when a restart wiped the one a button points to, the voice note is downloaded
# from WhatsApp again and transcribed again, for as long as Meta keeps it.
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


def split_text(text: str, limit: int = TEXT_BODY_MAX_CHARS) -> list[str]:
    """Cuts a text WhatsApp would refuse as too long into pieces, at a line break or a space when there is one."""
    pieces = []
    while len(text) > limit:
        # Only a break in the second half of the piece, so the pieces stay about as long as WhatsApp allows.
        cut = text.rfind('\n', limit // 2, limit + 1)
        if cut == -1:
            cut = text.rfind(' ', limit // 2, limit + 1)
        if cut == -1:
            cut = limit
        pieces.append(text[:cut].rstrip())
        text = text[cut:].lstrip()
    pieces.append(text)
    return pieces


def parse_reply_id(reply_id: str) -> tuple[str, str | None, str]:
    """(action, target language, media id) of a tapped button or a picked menu row. The target language is None
    but for a row of the translation menu, the media id is '' on buttons sent before it was added."""
    parts = reply_id.split(':')
    if len(parts) == 3 and parts[1] in LANGUAGE_LABELS:
        return parts[0], parts[1], parts[2]
    return parts[0], None, parts[1] if len(parts) > 1 else ''


def translation_languages(language: str) -> tuple[str, str]:
    """The language to translate into and the one to use when the text is already in it."""
    fallback = DEFAULT_LANGUAGE if language != DEFAULT_LANGUAGE else FALLBACK_TRANSLATION_LANGUAGE
    return (get_localized_message(language, 'language_name'),
            get_localized_message(fallback, 'language_name'))


def run_action(action: str, text: str, target: str = None) -> str:
    if action == 'correct':
        return correct_text(text)
    if action == 'summarize':
        return summarize_text(text)
    if action == 'translate':
        return translate_text(text, *translation_languages(target))
    raise ValueError(f"Unknown action '{action}'")


def action_from_typed_choice(text: str) -> str | None:
    choice = text.strip()
    if choice.isdigit() and 1 <= int(choice) <= len(ACTIONS):
        return ACTIONS[int(choice) - 1]
    return None


class MessageProcessor:
    def __init__(self):
        self.wa = WhatsAppAPI(mobile_id=MOBILE_ID, api_token=GRAPH_API_TOKEN, error_handler=raise_with_meta_error)
        # Kept in this process's memory: the Procfile runs a single gunicorn worker (with threads) so that a button
        # tap reaches the process that sent the transcription. A restart or a deploy still forgets them.
        self.user_to_language = {}
        self.user_to_transcriptions = {}

    def set_user_language(self, user_id: str, language: str):
        self.user_to_language[user_id] = language

    def get_user_language(self, user_id: str) -> str:
        return self.user_to_language.get(user_id) or language_for_wa_id(user_id)

    def set_user_transcription(self, user_id: str, message_id: str, text: str, transcription_message_id: str):
        """Remembers the transcription a message belongs to and the message that shows it, which answers reply to."""
        if user_id not in self.user_to_transcriptions:
            self.user_to_transcriptions[user_id] = {}
        self.user_to_transcriptions[user_id][message_id] = (text, transcription_message_id)

    def get_user_transcription(self, user_id: str, message_id: str) -> tuple[str, str | None]:
        return self.user_to_transcriptions.get(user_id, {}).get(message_id, ('', None))

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

    def send_text(self, to: str, text: str, reply_to: str) -> list[str]:
        """Sends text, in several messages each replying to the previous one if it is too long; returns their ids."""
        ids = []
        for piece in split_text(text):
            # Not saved to the wrapper's database: without one it would warn with the whole message in the logs.
            ret = self.wa.send_text(to, piece, reply_to_message_id=reply_to, save_to_db=False)
            reply_to = ret['messages'][0]['id']
            ids.append(reply_to)
        return ids

    def send_buttons(self, to: str, body: str, reply_to: str, language: str, media_id: str) -> str:
        """Sends body with one reply button per action and returns the id of the message."""
        data = MessageObject(to, reply_to_message_id=reply_to).base_data
        data['type'] = 'interactive'
        data['interactive'] = {
            'type': 'button',
            'body': {'text': body},
            'action': {'buttons': [
                {'type': 'reply', 'reply': {'id': f'{action}:{media_id}',
                                            'title': get_localized_message(language, f'{action}_button')}}
                for action in ACTIONS
            ]},
        }
        ret = self.wa._send_message(data, save_to_db=False)
        return ret['messages'][0]['id']

    def send_language_menu(self, to: str, reply_to: str, language: str, media_id: str) -> str:
        """Sends the list of languages to translate into and returns the id of the message."""
        data = MessageObject(to, reply_to_message_id=reply_to).base_data
        data['type'] = 'interactive'
        data['interactive'] = {
            'type': 'list',
            'body': {'text': get_localized_message(language, 'translate_menu_prompt')},
            'action': {
                'button': get_localized_message(language, 'translate_menu_button')[:BUTTON_TITLE_MAX_CHARS],
                'sections': [{
                    'title': get_localized_message(language, 'translate_menu_section')[:LIST_ROW_TITLE_MAX_CHARS],
                    'rows': [{'id': f'translate:{iso}:{media_id}', 'title': label[:LIST_ROW_TITLE_MAX_CHARS]}
                             for iso, label in LANGUAGE_LABELS.items()],
                }],
            },
        }
        ret = self.wa._send_message(data, save_to_db=False)
        return ret['messages'][0]['id']

    def send_transcription(self, to: str, transcription: str, reply_to: str, language: str,
                           media_id: str) -> list[str]:
        """Sends the transcription with the action buttons and returns the ids a reply can point to, the message
        that shows the transcription first."""
        header = get_localized_message(language, 'header')
        text = f'*{header}*\n\n{transcription}'
        if len(text) <= BUTTONS_BODY_MAX_CHARS:
            return [self.send_buttons(to, text, reply_to, language, media_id)]
        text_ids = self.send_text(to, text, reply_to)
        buttons_id = self.send_buttons(to, get_localized_message(language, 'actions_prompt'), text_ids[-1], language,
                                       media_id)
        return text_ids + [buttons_id]

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
        elif message_type == 'interactive' and message['interactive'].get('type') in ('button_reply', 'list_reply'):
            interactive = message['interactive']
            action, target, media_id = parse_reply_id(interactive[interactive['type']]['id'])
            self.process_action(message, wa_id, action, debug, media_id, target)
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
        log_outcome('audio', recipient_id, message_id, 'received', started)
        self.send_reaction(recipient_id, message_id, PROCESSING_REACTION)
        media_id = message['audio']['id']
        progress = []
        try:
            transcription = self.transcribe(media_id, progress)
            if not transcription:
                log_outcome('audio', recipient_id, message_id, 'empty transcription', started)
                self.send_reaction(recipient_id, message_id, FAILED_REACTION)
                return
            progress.append('reply')
            answer_ids = self.send_transcription(recipient_id, self.debug_prefix(transcription, debug), message_id,
                                                 language, media_id)
        except Exception as e:
            stage = progress[-1] if progress else 'download'
            log_outcome('audio', recipient_id, message_id, f'failed at {stage}', started, describe(e))
            self.send_reaction(recipient_id, message_id, FAILED_REACTION)
            raise
        for answer_id in answer_ids:
            self.set_user_transcription(wa_id, answer_id, transcription, answer_ids[0])
        self.send_reaction(recipient_id, message_id, DONE_REACTION)
        log_outcome('audio', recipient_id, message_id, 'ok', started,
                    f'{len(transcription)} chars, reply {short_id(answer_ids[-1])}')

    def transcribe(self, media_id: str, progress: list = None) -> str:
        """Downloads a voice note from WhatsApp and transcribes it; `progress` gets the stage being worked on."""
        progress = [] if progress is None else progress
        progress.append('download')
        media_file = self.wa.get_media(media_id)
        progress.append('convert')
        media_file_mp3 = convert_audio_to_mp3(media_file)
        progress.append('transcribe')
        return speech_to_text(media_file_mp3).strip()

    def transcribe_again(self, message: dict, wa_id: str, media_id: str, context_id: str) -> str:
        """The transcription of a voice note whose transcription a restart wiped from memory, '' if WhatsApp
        no longer gives the voice note. Any later failure (conversion, transcription) is raised."""
        recipient_id = message['from']
        message_id = message['id']
        started = time.monotonic()
        progress = []
        try:
            transcription = self.transcribe(media_id, progress)
        except Exception as e:
            stage = progress[-1] if progress else 'download'
            log_outcome('retranscribe', recipient_id, message_id, f'failed at {stage}', started, describe(e))
            if stage == 'download':
                return ''
            raise
        log_outcome('retranscribe', recipient_id, message_id, 'ok', started, f'{len(transcription)} chars')
        if transcription:
            # Answers reply to the buttons, the message that showed the transcription isn't known anymore.
            self.set_user_transcription(wa_id, context_id, transcription, context_id)
        return transcription

    def process_action(self, message: dict, wa_id: str, action: str, debug: bool, media_id: str = '',
                       target: str = None):
        """Runs a button's action on the transcription the button belongs to and replies to that transcription.
        Translate without a target language asks for one with a menu."""
        recipient_id = message['from']
        message_id = message['id']
        language = self.get_user_language(wa_id)
        started = time.monotonic()
        context_id = message.get('context', {}).get('id')
        transcription, transcription_message_id = self.get_user_transcription(wa_id, context_id)
        if not transcription and not (media_id and context_id):
            log_outcome(action, recipient_id, message_id, 'context not found', started)
            reply = get_localized_message(language, 'context_not_found')
            self.send_text(recipient_id, self.debug_prefix(reply, debug), message_id)
            return
        if action == 'translate' and target is None:
            # The menu needs no transcription: its rows carry the media id, picking one finds it again if needed.
            menu_reply_to = transcription_message_id or context_id
            menu_id = self.send_language_menu(recipient_id, menu_reply_to, language, media_id)
            if transcription:
                self.set_user_transcription(wa_id, menu_id, transcription, transcription_message_id)
            log_outcome(action, recipient_id, message_id, 'menu', started)
            return
        self.send_reaction(recipient_id, message_id, WORKING_REACTION)
        label = f'{action} {target}' if target else action
        try:
            if not transcription:
                transcription = self.transcribe_again(message, wa_id, media_id, context_id)
                transcription_message_id = context_id
            if not transcription:
                log_outcome(label, recipient_id, message_id, 'context not found', started)
                self.send_reaction(recipient_id, message_id, FAILED_REACTION)
                reply = get_localized_message(language, 'context_not_found')
                self.send_text(recipient_id, self.debug_prefix(reply, debug), message_id)
                return
            result = run_action(action, transcription, target or language)
            title = f"*{get_localized_message(language, f'{action}_header')}*"
            if target:
                title = f'{title} ({LANGUAGE_LABELS[target]})'
            self.send_text(recipient_id, self.debug_prefix(f'{title}\n\n{result}', debug), transcription_message_id)
        except Exception as e:
            log_outcome(label, recipient_id, message_id, 'failed', started, describe(e))
            self.send_reaction(recipient_id, message_id, FAILED_REACTION)
            self.send_failure(recipient_id, message_id, language)
            return
        self.send_reaction(recipient_id, message_id, DONE_REACTION)
        log_outcome(label, recipient_id, message_id, 'ok', started, f'{len(result)} chars')

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
