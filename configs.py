import os

from dotenv import load_dotenv

load_dotenv()

GRAPH_API_TOKEN = os.getenv('GRAPH_API_TOKEN')
MOBILE_ID = os.getenv('MOBILE_ID')

DEBUG_CHAT_IDS = os.getenv('DEBUG_CHAT_IDS', '').split(',')
