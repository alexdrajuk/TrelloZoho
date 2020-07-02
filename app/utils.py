import json
import re
import settings
import logging

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


def is_exchange(trello_comment):
    comment_entities = trello_comment.get('data').get('text').split(settings.ENTITIES_DIVISOR)
    if comment_entities[0].lower() == settings.EXCHANGE_PREFIX.lower():
        return True
    return False


def is_transfer(trello_comment):
    comment_entities = trello_comment.get('data').get('text').split(settings.ENTITIES_DIVISOR)
    if comment_entities[0].lower() == settings.TRANSFER_PREFIX.lower():
        return True
    return False


def extract_exchange_data(trello_comment):
    comment_entities = trello_comment.get('data').get('text').split(settings.ENTITIES_DIVISOR)
    sell, buy = comment_entities[0].split('-')

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


def extract_comment_data(trello_comment):
    comment_entities = trello_comment.get('data').get('text').split(settings.ENTITIES_DIVISOR)
    comment_data = {
        'expense_account': comment_entities[0],
        'expense_amount': comment_entities[1],
    }
    if len(comment_entities) == 2:
        return comment_data

    elif len(comment_entities) == 4 and comment_entities[2] in settings.CARD_PREFIXES:
        comment_data['card'] = comment_entities[2]
        comment_data['note'] = comment_entities[3]

    elif len(comment_entities) == 3 and comment_entities[2] in settings.CARD_PREFIXES:
        comment_data['card'] = comment_entities[2]

    elif len(comment_entities) == 3 and comment_entities[2] not in settings.CARD_PREFIXES:
        comment_data['note'] = comment_entities[2]

    else:
        raise Exception(f"Comment {trello_comment.get('data').get('text')} can't be processed")

    return comment_data
