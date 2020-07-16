from datetime import datetime as dt
from datetime import timedelta
import logging

import requests
from pprint import pprint

from zohotrello import settings
from zohotrello import utils
from zohotrello.trello_api import TrelloAPI

logger = logging.getLogger('appLogger')


class ZohoAPI:
    def __init__(self, client_id, client_secret, redirect_uri, refresh_token, organization_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token
        self.organization_id = organization_id
        self._access_token = None
        self._access_token_expires_at = None

    @property
    def access_token(self):
        if self._access_token and self._access_token_expires_at and self._access_token_expires_at > dt.now():
            return self._access_token
        self.refresh_access_token()
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value

    def refresh_access_token(self):
        url = 'https://accounts.zoho.com/oauth/v2/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        query = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'refresh_token': self.refresh_token,
        }
        # Stupid ZOHO API requires querystring in POST request
        response = requests.post(url, headers=headers, params=query, timeout=settings.REQUESTS_TIMEOUT)
        response.raise_for_status()

        if 'error' in response.json():
            logger.error(response.json().get('error'))
            raise Exception('Error during refresh_access_token')

        expires_in = int(response.json().get('expires_in'))
        access_token = response.json().get('access_token')

        self._access_token = access_token
        # Just for case it updates access_token five minutes before the expiration time
        self.access_token_expires_at = dt.now() + timedelta(seconds=expires_in - 300)

    def get_currency_by_code(self, currency_code):
        url = "https://books.zoho.com/api/v3/settings/currencies"
        headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        query = {
            'organization_id': self.organization_id,
        }
        response = requests.get(url, headers=headers, params=query, timeout=settings.REQUESTS_TIMEOUT)
        response.raise_for_status()

        for currency in response.json().get('currencies'):
            if currency.get('currency_code').lower() == currency_code.lower():
                return currency

    def fetch_accounts_list(self, only_active=True):
        url = 'https://books.zoho.com/api/v3/chartofaccounts'
        headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        query = {
            'organization_id': self.organization_id,
        }
        if only_active:
            query['filter_by'] = 'AccountType.Active'

        response = requests.get(url, headers=headers, params=query, timeout=settings.REQUESTS_TIMEOUT)
        response.raise_for_status()

        return response.json().get('chartofaccounts')

    def fetch_bank_accounts(self, only_active=True):
        url = "https://books.zoho.com/api/v3/bankaccounts"
        headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        query = {
            'organization_id': self.organization_id,
        }
        if only_active:
            query['filter_by'] = 'Status.Active'

        response = requests.get(url, headers=headers, params=query, timeout=60)
        response.raise_for_status()
        if response.json().get('message') == 'success':
            return response.json().get('bankaccounts')

    def get_bank_account_by_name(self, account_name):
        bank_accounts = self.fetch_bank_accounts()
        for account in bank_accounts:
            if account.get('account_name').lower() == account_name.lower():
                return account

    def get_expense_account_by_name(self, account_name, only_active=True):
        url = "https://books.zoho.com/api/v3/chartofaccounts"
        headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json',
        }
        query = {
            'organization_id': self.organization_id,
            'account_type': 'expense',
        }
        if only_active:
            query['filter_by'] = 'AccountType.Active'

        response = requests.get(url, headers=headers, params=query, timeout=settings.REQUESTS_TIMEOUT)
        response.raise_for_status()

        if response.json().get('message') != 'success':
            return None

        accounts = response.json().get('chartofaccounts')
        for account in accounts:
            if account.get('account_name').lower() == account_name.lower():
                return account

    def create_bank_transaction(self, **kwargs):
        url = "https://books.zoho.com/api/v3/banktransactions"
        headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json',
        }
        query = {
            'organization_id': self.organization_id,
        }
        body = kwargs
        response = requests.post(url, headers=headers, params=query, json=kwargs, timeout=settings.REQUESTS_TIMEOUT)
        response.raise_for_status()
        response_code = response.json().get('code')
        if response_code and response_code != 0:
            logger.error(f"code: {response_code} - {response.json().get('message')}")
            raise Exception('The bank transaction has not been recorded.')

    def create_exchange_transaction(self, comment_text):
        exchange_data = utils.extract_exchange_data(comment_text)

        account_from = settings.ACCOUNTS_BY_CURRENCY_KS.get(exchange_data.get('sell_currency'))
        account_to = settings.ACCOUNTS_BY_CURRENCY_KS.get(exchange_data.get('buy_currency'))

        transaction_data = {
            'from_account_id': self.get_bank_account_by_name(account_from).get('account_id'),
            'to_account_id': self.get_bank_account_by_name(account_to).get('account_id'),
            'transaction_type': 'transfer_fund',
            'amount': exchange_data.get('sell_amount'),
            'exchange_rate': round(exchange_data.get('sell_amount') / exchange_data.get('buy_amount'), 6),
            'reference_number': 'API test'
        }
        self.create_bank_transaction(**transaction_data)

    def create_assistant_transaction(self, comment_text):
        expense_data = utils.extract_comment_entities(comment_text)
        expense_amount = int(''.join(s for s in expense_data.get('expense_amount') if s.isnumeric()))
        account_from = None
        account_to = None
        currency_id = None

        if utils.is_usd_amount(expense_data.get('expense_amount')):
            expense_data['expense_account'] = settings.ACCOUNTS_BY_CURRENCY_ASSIST.get('usd')
            account_from = settings.ACCOUNTS_BY_CURRENCY_KS.get('usd')
            account_to = settings.ACCOUNTS_BY_CURRENCY_ASSIST.get('usd')
            currency_id = self.get_currency_by_code('usd').get('currency_id')

        elif utils.is_eur_amount(expense_data.get('expense_amount')):
            expense_data['expense_account'] = settings.ACCOUNTS_BY_CURRENCY_ASSIST.get('eur')
            account_from = settings.ACCOUNTS_BY_CURRENCY_KS.get('eur')
            account_to = settings.ACCOUNTS_BY_CURRENCY_ASSIST.get('eur')
            currency_id = self.get_currency_by_code('eur').get('currency_id')

        else:
            expense_data['expense_account'] = settings.ACCOUNTS_BY_CURRENCY_ASSIST.get('uah')
            account_from = settings.ACCOUNTS_BY_CURRENCY_KS.get('uah')
            account_to = settings.ACCOUNTS_BY_CURRENCY_ASSIST.get('uah')
            currency_id = self.get_currency_by_code('uah').get('currency_id')

        transaction_data = {
            'from_account_id': self.get_bank_account_by_name(account_from).get('account_id'),
            'to_account_id': self.get_bank_account_by_name(account_to).get('account_id'),
            'transaction_type': 'transfer_fund',
            'amount': expense_amount,
            'reference_number': 'API test',
            'currency_id': currency_id
        }
        if expense_data.get('note'):
            transaction_data.update({'reference_number': expense_data.get('note')})
        pprint(transaction_data)
        self.create_bank_transaction(**transaction_data)





client_id = settings.ZOHO_CLIENT_ID
client_secret = settings.ZOHO_CLIENT_SECRET
redirect_uri = settings.ZOHO_REDIRECT_URI
refresh_token = settings.ZOHO_REFRESH_TOKEN
organization_id = settings.ZOHO_ORGANIZATION_ID


# zoho_api = ZohoAPI(client_id, client_secret, redirect_uri, refresh_token, organization_id)
# account = zoho_api.get_bank_account_by_name(settings.ACCOUNTS_BY_CURRENCY_KS.get('usd'))


# api_key = settings.TRELLO_API_KEY
# api_token = settings.TRELLO_API_TOKEN
# board_name = settings.TRELLO_BOARD_NAME
# card_name = settings.TRELLO_CARD_NAME

# trello_api = TrelloAPI(api_key, api_token)
# card_id = trello_api.get_card_on_board_by_name(board_name, card_name).get('id')
# # print(trello_api.get_card_comments(card_id))
# new_comments = trello_api.fetch_new_comments(board_name, card_name)
# comment = [comment for comment in new_comments if comment.get('id') == '5ef08fda5d26be211d4dabd7'][0]
# # trello_api.save_initial_comment_date(card_id)
# # pprint(comment)

# comment_text = comment.get('data').get('text')
# zoho_api.create_exchange_transaction('exchange::$100-2000')
