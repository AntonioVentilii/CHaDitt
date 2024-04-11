import json

from whatsapp_wrapper import WhatsAppAPI
from whatsapp_wrapper.audio_utilities import convert_audio_to_mp3

from configs import DEBUG_CHAT_IDS, GRAPH_API_TOKEN, MOBILE_ID
from openai_wrapper.audio import speech_to_text
from openai_wrapper.chat import correct_text, summarize_text
from openai_wrapper.language import get_intended_language_iso
from translations import DEFAULT_LANGUAGE, check_supported_language, get_localized_message


class MessageProcessor:
    def __init__(self):
        self.wa = WhatsAppAPI(mobile_id=MOBILE_ID, api_token=GRAPH_API_TOKEN)
        self.user_to_language = {}
        self.user_to_messages = {}

    def set_user_language(self, user_id: str, language: str):
        self.user_to_language[user_id] = language

    def get_user_language(self, user_id: str) -> str:
        return self.user_to_language.get(user_id, DEFAULT_LANGUAGE)

    def set_user_message(self, user_id: str, message_id: str, text: str):
        if user_id not in self.user_to_messages:
            self.user_to_messages[user_id] = {}
        self.user_to_messages[user_id][message_id] = text

    def get_user_message(self, user_id: str, message_id: str) -> str:
        return self.user_to_messages.get(user_id, {}).get(message_id, '')

    def process_webhook_post_request(self, data, mark_message_as_read: bool = True, debug: bool = False) -> dict:
        if not debug:
            print(f"Webhook request received:\n{json.dumps(data, indent=2)}")
        wa = self.wa
        entry = data['entry'][0]
        changes = entry['changes']
        last_change = changes[0]['value']
        if 'messages' not in last_change:
            print("No messages found in last change")
            return {'success': True}
        message = last_change['messages'][0]
        wa_id = last_change['contacts'][0]['wa_id']
        language = self.get_user_language(wa_id)
        loc = lambda key, **kwargs: get_localized_message(language, key, **kwargs)
        message_type = message['type']
        recipient_id = message['from']
        if debug and recipient_id not in DEBUG_CHAT_IDS:
            print(f"User {recipient_id} is not in debug chat ids. Ignoring message.")
            return {'success': True}
        banned_users = wa.banned_users
        if recipient_id in banned_users:
            print(f"User {recipient_id} is banned. Ignoring message.")
            return {'success': True}
        message_id = message['id']
        if mark_message_as_read:
            wa.mark_as_read(message_id)
        if message_type == 'audio':
            awaiting_msg = loc('audio_processing')
            awaiting_msg = f"*DEBUG*: {awaiting_msg}" if debug else awaiting_msg
            wa.send_text(recipient_id, awaiting_msg)
            media_id = message['audio']['id']
            print(f"Audio message received from {recipient_id}: {media_id}")
            media_file = wa.get_media(media_id)
            media_file_mp3 = convert_audio_to_mp3(media_file)
            text = speech_to_text(media_file_mp3)
            self.set_user_message(wa_id, message_id, text)
            header = loc('header')
            footer = loc('footer')
            response_msg = f'*{header}*:\n\n{text}\n\n_{footer}_'
        elif message_type == 'text':
            incoming_msg = message['text']['body']
            print(f"Message received from {recipient_id}: {incoming_msg}")
            context_id = message.get('context', {}).get('id')
            if context_id:
                try:
                    choice = int(incoming_msg.lower().strip())
                except ValueError:
                    choice = None
                context_msg = self.get_user_message(wa_id, context_id)
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
            response_msg = loc('unsupported_content', message_type=message_type)

        if debug:
            response_msg = f"*DEBUG*: {response_msg}"

        wa.send_text(recipient_id, response_msg, reply_to_message_id=message_id)
        if mark_message_as_read:
            wa.mark_as_read(message_id)

        return {'success': True}
