import os
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

GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
DIALOGFLOW_SESSION_ID = os.getenv('DIALOGFLOW_SESSION_ID')

COMMENT_PARTS_DIVISOR = '::'
EXCHANGE_PREFIX = 'exchange'
EXCHANGE_CURRENCIES = {'$': 'usd', 'e': 'eur', 'eur': 'eur', 'uah': 'uah'}
TRANSFER_PREFIX = 'transfer'
CARD_PREFIXES = ('ukrsib', 'ukrsib', 'укрсиб', 'укрсибб')
DEFAULT_CURRENCY = 'uah'

ASSISTANT_NAME = 'Anna'

ACCOUNTS_BY_CURRENCY_KS = {
    'uah': 'CASH UAH - KS',
    'eur': 'CASH EUR - KS',
    'usd': 'CASH USD - KS',
}

ACCOUNTS_BY_CURRENCY_ASSIST = {
    'uah': 'KASSA UAH - Anna',
    'eur': 'KASSA EUR - Anna',
    'usd': 'KASSA USD - Anna',
}

EXPENSE_ACCOUNTS = {
    'automobile': 'Automobile Expense',
    'clothes': 'Clothes',
    'charity': 'Charity',
    'entertainment': 'Meals and Entertainment',
    'family': 'family',
    'fuel': 'Fuel/Mileage Expenses',
    'gifts': 'Gifts',
    'gift': 'Gifts',
    'health': 'Health&Beauty',
    'household': 'Household',
    'house': 'Household',
    'it': 'IT and Internet Expenses',
    'internet': 'IT and Internet Expenses',
    'leisure': 'Leisure&Fun',
    'meals': 'Meals and Entertainment',
    'parking': 'Parking',
    'rent': 'Rent Expense',
    'Repairs and Maintenance': 'Repairs and Maintenance',
    'self': 'Self Development',
    'self dev': 'Self Development',
    'selfdev': 'Self Development',
    'taxi': 'Taxi',
    'th': 'TH',
    'tips': 'Tips expense',
}


log_config = {
    'version': 1,
    'handlers': {
        'fileHandler': {
            'class': 'logging.FileHandler',
            'formatter': 'commonFormatter',
            'filename': '../logs.log',
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
