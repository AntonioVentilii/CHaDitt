import os

from dotenv import load_dotenv

load_dotenv()

GRAPH_API_TOKEN = os.getenv('GRAPH_API_TOKEN')
MOBILE_ID = os.getenv('MOBILE_ID')
ENCODED_DB_CREDENTIALS_JSON = os.getenv('ENCODED_DB_CREDENTIALS_JSON')
BACKUP_FOLDER = os.getenv('BACKUP_FOLDER')
