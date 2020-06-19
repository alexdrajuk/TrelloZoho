import os
import re
import logging
import logging.config

from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')

TRELLO_BOARD_NAME = os.getenv('TRELLO_BOARD_NAME')
TRELLO_CARD_NAME = os.getenv('TRELLO_CARD_NAME')
CARD_COMMENTS_LIMIT = 30

REQUESTS_TIMEOUT = 60

ZOHO_ORGANIZATION_ID = os.getenv('ZOHO_ORGANIZATION_ID')
ZOHO_REFRESH_TOKEN = os.getenv('ZOHO_REFRESH_TOKEN')
ZOHO_CLIENT_ID = os.getenv('ZOHO_CLIENT_ID')
ZOHO_CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET')
ZOHO_REDIRECT_URI = os.getenv('ZOHO_REDIRECT_URI')

accounts_regexes {
    'Automobile Expense': (re.compile(), ),
    'Meals and Entertainment': re.compile(),
    'Leisure&Fun': re.compile(),
    'Parking': re.compile(),
    'Household': re.compile(),
    'Health&Beauty': re.compile(),
}


log_config = {
    'version': 1,
    'handlers': {
        'fileHandler': {
            'class': 'logging.FileHandler',
            'formatter': 'commonFormatter',
            'filename': 'logs.log',
        }
    },
    'formatters': {
        'commonFormatter': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        }
    },
    'loggers': {
        'appLogger': {
            'handlers': ["fileHandler"],
            'level': 'INFO'
        }
    }
}

logging.config.dictConfig(log_config)
