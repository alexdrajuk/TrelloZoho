import os

from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')

TRELLO_BOARD_NAME = os.getenv('TRELLO_BOARD_NAME')
TRELLO_CARD_NAME = os.getenv('TRELLO_CARD_NAME')
CARD_COMMENTS_LIMIT = 10
