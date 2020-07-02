from datetime import datetime as dt
from datetime import timedelta
import logging

import requests

import settings
import utils
from pprint import pprint
from trello_api import TrelloAPI

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

        response = requests.get(url, headers=headers, params=query)
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

        response = requests.get(url, headers=headers, params=query)
        response.raise_for_status()
        if response.json().get('message') == 'success':
            return response.json().get('bankaccounts')

    def get_bank_account_by_name(self, account_name):
        bank_accounts = self.fetch_bank_accounts()
        for account in bank_accounts:
            if account.get('account_name').lower() == account_name.lower():
                return account

    def get_expense_account_id(self, account_name):
        pass


    def create_bank_transaction(self, **kwargs):
        url = "https://books.zoho.com/api/v3/banktransactions"
        headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json',
        }
        params = {
            'organization_id': self.organization_id,
        }
        response = requests.post(url, headers=headers, params=params, json=kwargs)
        response.raise_for_status()
        response_code = response.json().get('code')
        if response_code and response_code != 0:
            logger.error(f"code: {response_code} - {response.json().get('message')}")
            raise Exception('The bank transaction has not been recorded.')


    def create_exchange_transaction(self, trello_comment):
        exchange_data = utils.extract_exchange_data(trello_comment)

        account_from = settings.ACCOUNTS_BY_CURRENCY_KS.get(exchange_data.get('sell_currency'))
        account_to = settings.ACCOUNTS_BY_CURRENCY_KS.get(exchange_data.get('buy_currency'))

        transaction_data = {
            'from_account_id': self.get_bank_account_by_name(account_from).get('account_id'),
            'to_account_id': self.get_bank_account_by_name(account_to).get('account_id'),
            'transaction_type': 'transfer_fund',
            'amount': exchange_data.get('sell_amount'),
            'exchange_rate': round(exchange_data.get('sell_amount') / exchange_data.get('buy_amount'), 6)
        }
        self.create_bank_transaction(**transaction_data)
