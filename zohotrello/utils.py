import json
import re
import logging

from zohotrello import settings

logger = logging.getLogger('app_logger')


def save_value(key, value):
    with open('./db.json', 'r') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            data = {}

    data[key] = value

    with open('./db.json', mode='w') as f:
        json.dump(data, f)


def load_value(key):
    with open('./db.json') as f:
        try:
            data = json.load(f)
            return data.get(key)
        except (json.decoder.JSONDecodeError, KeyError):
            return None


def is_exchange(comment_text):
    comment_entities = comment_text.split(settings.COMMENT_PARTS_DIVISOR)
    return comment_entities[0].lower() == settings.EXCHANGE_PREFIX.lower()


def is_transfer(comment_text):
    comment_entities = comment_text.split(settings.COMMENT_PARTS_DIVISOR)
    return comment_entities[0].lower() == settings.TRANSFER_PREFIX.lower()


def is_expense(comment_text):
    comment_entities = comment_text.split(settings.COMMENT_PARTS_DIVISOR)
    return comment_entities[0].lower() in settings.EXPENSE_ACCOUNTS.keys()


def is_assistant_transfer(comment_text):
    comment_entities = comment_text.split(settings.COMMENT_PARTS_DIVISOR)
    return comment_entities[0].lower() == settings.ASSISTANT_NAME.lower()


def is_usd_amount(amount_entity):
    return amount_entity.startswith('$')


def is_eur_amount(amount_entity):
    return 'eur' in amount_entity.lower()


def extract_exchange_data(comment_text):
    comment_entities = comment_text.split(settings.COMMENT_PARTS_DIVISOR)
    sell, buy = comment_entities[1].split('-')

    sell_currency = [v for k, v in settings.EXCHANGE_CURRENCIES.items() if k in sell]
    sell_currency = sell_currency[0] if sell_currency else settings.DEFAULT_CURRENCY
    sell_amount = int(''.join(s for s in sell if s.isnumeric()))

    buy_currency = [v for k, v in settings.EXCHANGE_CURRENCIES.items() if k in buy]
    buy_currency = buy_currency[0] if buy_currency else settings.DEFAULT_CURRENCY
    buy_amount = int(''.join(b for b in buy if b.isnumeric()))

    return {
        'sell_amount': sell_amount,
        'sell_currency': sell_currency,
        'buy_amount': buy_amount,
        'buy_currency': buy_currency,
    }


def extract_comment_entities(comment_text):
    comment_parts = comment_text.split(settings.COMMENT_PARTS_DIVISOR)
    comment_entities = {
        'expense_account': comment_parts[0],
        'expense_amount': comment_parts[1],
    }
    if len(comment_parts) == 2:
        return comment_entities

    elif len(comment_parts) == 4 and comment_parts[2] in settings.CARD_PREFIXES:
        comment_entities['card'] = comment_parts[2]
        comment_entities['note'] = comment_parts[3]

    elif len(comment_parts) == 3 and comment_parts[2] in settings.CARD_PREFIXES:
        comment_entities['card'] = comment_parts[2]

    elif len(comment_parts) == 3 and comment_parts[2] not in settings.CARD_PREFIXES:
        comment_entities['note'] = comment_parts[2]

    else:
        raise Exception(f"Comment {comment_text} can't be processed")

    return comment_entities
    

