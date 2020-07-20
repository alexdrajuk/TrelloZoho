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


def clear_amount(amount):
    pattern = r'[^\d,.]+'
    return float(re.sub(pattern, '', str(amount)))


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


def is_uah_amount(amount_entity):
    return not any([
        is_eur_amount(amount_entity),
        is_usd_amount(amount_entity),
    ])


def is_paid_by_card(comment_text):
    comment_entities = extract_comment_entities(comment_text)
    return 'card' in comment_entities and comment_entities.get('card').lower() in settings.CARD_PREFIXES


def is_out_of_pattern(comment_text):
    return not any(regex.match(comment_text) for regex in settings.COMMENT_PATTERNS)


def is_checking_balance(comment_text):
    comment_parts = comment_text.split(settings.COMMENT_PARTS_DIVISOR)
    return comment_parts[0].lower() in settings.BALANCE_PREFIXES



# def is_balance_equal(comment_text, account_balance):
#     comment_entities = extract_comment_entities(comment_text)
#     cash = comment_entities.get('expense_amount')
#     cash = float(''.join(s for s in cash if s.isnumeric()))


def extract_exchange_data(comment_text):
    comment_entities = comment_text.split(settings.COMMENT_PARTS_DIVISOR)
    sell, buy = comment_entities[1].split('-')

    sell_currency = [v for k, v in settings.EXCHANGE_CURRENCIES.items() if k in sell]
    sell_currency = sell_currency[0] if sell_currency else settings.DEFAULT_CURRENCY
    sell_amount = clear_amount(sell)

    buy_currency = [v for k, v in settings.EXCHANGE_CURRENCIES.items() if k in buy]
    buy_currency = buy_currency[0] if buy_currency else settings.DEFAULT_CURRENCY
    buy_amount = clear_amount(buy)

    note = comment_entities[2] if len(comment_entities) >= 2 else ''

    return {
        'sell_amount': sell_amount,
        'sell_currency': sell_currency,
        'buy_amount': buy_amount,
        'buy_currency': buy_currency,
        'reference_number': note,
    }


def extract_comment_entities(comment_text):
    comment_parts = comment_text.split(settings.COMMENT_PARTS_DIVISOR)
    comment_entities = {
        'expense_account': comment_parts[0],
        'expense_amount': comment_parts[1],
    }
    if len(comment_parts) == 2:
        return comment_entities

    elif len(comment_parts) == 4 and comment_parts[2].lower() in settings.CARD_PREFIXES:
        comment_entities['card'] = comment_parts[2]
        comment_entities['note'] = comment_parts[3]

    elif len(comment_parts) == 3 and comment_parts[2].lower() in settings.CARD_PREFIXES:
        comment_entities['card'] = comment_parts[2]

    elif len(comment_parts) == 3 and comment_parts[2].lower() not in settings.CARD_PREFIXES:
        comment_entities['note'] = comment_parts[2]

    else:
        raise Exception(f"Comment {comment_text} can't be processed")

    return comment_entities


def send_notification(text):
    print(f'Комментарий: {text} не обработан')
