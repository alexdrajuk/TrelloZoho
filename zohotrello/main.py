from zohotrello import settings
import utils
from trello_api import TrelloAPI
from zoho_api import ZohoAPI

from pprint import pprint

TrelloAPI = TrelloAPI(settings.TRELLO_API_KEY, settings.TRELLO_API_TOKEN)
ZohoAPI = ZohoAPI(
    client_id=settings.ZOHO_CLIENT_ID,
    client_secret=settings.ZOHO_CLIENT_SECRET,
    redirect_uri=settings.ZOHO_REDIRECT_URI,
    refresh_token=settings.ZOHO_REFRESH_TOKEN,
    organization_id=settings.ZOHO_ORGANIZATION_ID
)

# new_comments = TrelloAPI.fetch_new_comments(settings.TRELLO_BOARD_NAME, settings.TRELLO_CARD_NAME)
new_comments = [
    # 'family::100::Cookies (API TEST)',
    # 'automobile::$100::gasoline (API TEST)',
    # 'meals::100eur::Сильпо (API TEST)',
    # 'family::100::Cookies (API TEST)',
    # 'health::$100::Pills (API TEST)',
    # 'exchange::$100-2500::exchange (API TEST)',
    # 'Anna::2500::Anna transfer (API TEST)',
    # 'O::2500::balance checking (API TEST)',
    'balance::1250::balance checking (API TEST)',
]
for comment_text in new_comments:
    if utils.is_expense(comment_text):
        ZohoAPI.create_expense_record(comment_text)
        continue
    if utils.is_assistant_transfer(comment_text):
        ZohoAPI.create_assistant_transaction(comment_text)
        continue
    if utils.is_exchange(comment_text):
        ZohoAPI.create_exchange_transaction(comment_text)
    if utils.is_checking_balance(comment_text):
        balance = utils.clear_amount(ZohoAPI.get_balance(comment_text))

        cash = utils.extract_comment_entities(comment_text).get('expense_amount')
        cash_amount = utils.clear_amount(cash)

        diff = balance - cash_amount
        amount = ''
        if diff != 0:
            if utils.is_usd_amount(cash):
                amount = f'${diff}'
            elif utils.is_eur_amount(cash):
                amount = f'{diff}eur'
            else:
                amount = diff
            print(amount)
            ZohoAPI.create_expense_record(f'unknown::{amount}::разница из остатка')
        continue
    else:
        utils.send_notification(comment_text)
