import json

from whatsapp_wrapper import WhatsAppAPI
from whatsapp_wrapper.audio_utilities import convert_audio_to_mp3

from configs import GRAPH_API_TOKEN, MOBILE_ID
from openai_wrapper.audio import speech_to_text
from openai_wrapper.language import get_intended_language_iso
from translations import DEFAULT_LANGUAGE, check_supported_language, get_localized_message


class MessageProcessor:
    def __init__(self):
        self.wa = WhatsAppAPI(mobile_id=MOBILE_ID, api_token=GRAPH_API_TOKEN)
        self.user_to_language = {}

    def set_user_language(self, user_id: str, language: str):
        self.user_to_language[user_id] = language

    def get_user_language(self, user_id: str) -> str:
        return self.user_to_language.get(user_id, DEFAULT_LANGUAGE)

    def process_webhook_post_request(self, data, mark_message_as_read: bool = True, debug: bool = False) -> dict:
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
        message_type = message['type']
        recipient_id = message['from']
        banned_users = wa.banned_users
        if recipient_id in banned_users:
            print(f"User {recipient_id} is banned. Ignoring message.")
            return {'success': True}
        message_id = message['id']
        if mark_message_as_read:
            wa.mark_as_read(message_id)
        if message_type == 'audio':
            if not debug:
                awaiting_msg = get_localized_message(language, 'audio_processing')
                wa.send_text(recipient_id, awaiting_msg)
            media_id = message['audio']['id']
            print(f"Audio message received from {recipient_id}: {media_id}")
            media_file = wa.get_media(media_id)
            media_file_mp3 = convert_audio_to_mp3(media_file)
            response_msg = speech_to_text(media_file_mp3)
        elif message_type == 'text':
            incoming_msg = message['text']['body']
            print(f"Message received from {recipient_id}: {incoming_msg}")
            iso_code = get_intended_language_iso(incoming_msg)
            success, response_msg = check_supported_language(iso_code, language)
            if success:
                self.user_to_language[wa_id] = iso_code
        else:
            response_msg = get_localized_message(language, 'unsupported_content', message_type=message_type)

        if debug:
            print(f"Response message: {response_msg}")
        else:
            wa.send_text(recipient_id, response_msg, reply_to_message_id=message_id)
            if mark_message_as_read:
                wa.mark_as_read(message_id)

        return {'success': True}
