from datetime import datetime as dt
from datetime import timedelta
import logging

import requests

import settings
import utils

logger = logging.getLogger('appLogger')


class ZohoAPI:
    def __init__(self, client_id, client_secret, redirect_uri, refresh_token, organization_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token
        self.organization_id = organization_id
        self.access_token = None
        self.access_token_expires_at = None

    @property
    def access_token(self):
        if self._access_token and self._access_token_expires_at > dt.now():
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

    def get_expense_account_id(self, account_name):
        pass
