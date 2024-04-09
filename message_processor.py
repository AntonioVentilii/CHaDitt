import json
import time

from requests import Response
from whatsapp_wrapper import WhatsAppAPI

from audio_utils import convert_audio_to_mp3
from configs import GRAPH_API_TOKEN, MOBILE_ID
from openai_wrapper.audio import speech_to_text


def whatsapp_error_handler(api_instance: WhatsAppAPI, response: Response, data: dict):
    ret = response.json()
    print(f"Failed to send request!\nError:\n{json.dumps(ret, indent=2)}\nData:\n{json.dumps(data, indent=2)}")
    error_code = ret.get('error', {}).get('code')
    if error_code == 131056:
        # (#131056) (Business Account, Consumer Account) pair rate limit hit
        # Message failed to send because there were too many messages sent from this phone number to the same phone
        # number in a short period of time.
        user_id = data['to']
        data = {
            "phone_number_id": user_id,
            "reason": "Rate limit hit",
            "timestamp": time.time(),
        }
        api_instance.db.add_banned_user(data, user_id)
    raise Exception(f"Failed to send request! Status code: {response.status_code}")


wa = WhatsAppAPI(mobile_id=MOBILE_ID, api_token=GRAPH_API_TOKEN, error_handler=whatsapp_error_handler)


def process_webhook_post_request(data, mark_message_as_read: bool = True, debug: bool = False) -> dict:
    print(f"Webhook request received:\n{json.dumps(data, indent=2)}")
    entry = data['entry'][0]
    changes = entry['changes']
    last_change = changes[0]['value']
    if 'messages' not in last_change:
        print("No messages found in last change")
        return {'success': True}
    message = last_change['messages'][0]
    wa_id = last_change['contacts'][0]['wa_id']
    wa.save_message_to_db(message, wa_id)
    message_type = message['type']
    recipient_id = message['from']
    banned_users = wa.db.list_banned_user_names()
    if recipient_id in banned_users:
        print(f"User {recipient_id} is banned. Ignoring message.")
        return {'success': True}
    message_id = message['id']
    if message_type == 'audio':
        if not debug:
            awaiting_msg = "Sto trasformando il tuo messaggio audio in testo. Attendere prego..."
            wa.send_text(recipient_id, awaiting_msg)
        media_id = message['audio']['id']
        print(f"Audio message received from {recipient_id}: {media_id}")
        media_file = wa.get_media(media_id)
        media_file_mp3 = convert_audio_to_mp3(media_file)
        response_msg = speech_to_text(media_file_mp3)
    else:
        response_msg = (f"Sorry, my only purpose is to process audio messages. "
                        f"I can't process {message_type} yet.")

    if debug:
        print(f"Response message: {response_msg}")
    else:
        wa.send_text(recipient_id, response_msg, reply_to_message_id=message_id)
        if mark_message_as_read:
            wa.mark_as_read(message_id)

    return {'success': True}
