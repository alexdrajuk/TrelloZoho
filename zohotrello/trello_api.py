from datetime import datetime as dt

import requests

from zohotrello import settings
from zohotrello import utils


class TrelloAPI:
    def __init__(self, api_key, api_token):
        self.api_key = api_key
        self.api_token = api_token

    def get_boards(self):
        url = 'https://api.trello.com/1/members/me/boards'
        headers = {
            "Accept": "application/json"
        }
        query = {
            'key': self.api_key,
            'token': self.api_token,
            'fields': 'name',
        }
        response = requests.get(url, headers=headers, params=query, timeout=settings.REQUESTS_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def get_board_by_name(self, board_name):
        for board in self.get_boards():
            if board.get('name').lower() == board_name.lower():
                return board

    def get_cards_on_board(self, board_id):
        url = f'https://api.trello.com/1/boards/{board_id}/cards'
        headers = {
            "Accept": "application/json"
        }
        query = {
            'key': self.api_key,
            'token': self.api_token,
        }
        response = requests.get(url, headers=headers, params=query, timeout=settings.REQUESTS_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def get_card_on_board_by_name(self, board_name, card_name):
        board_id = self.get_board_by_name(board_name).get('id')
        cards = self.get_cards_on_board(board_id)
        for card in cards:
            if card.get('name').lower() == card_name.lower():
                return card

    def get_card_comments(self, card_id, limit=settings.CARD_COMMENTS_LIMIT):
        url = f'https://api.trello.com/1/cards/{card_id}/actions'
        headers = {
            "Accept": "application/json"
        }
        query = {
            'key': self.api_key,
            'token': self.api_token,
        }
        response = requests.get(url, headers=headers, params=query, timeout=settings.REQUESTS_TIMEOUT)
        response.raise_for_status()
        comments = [action for action in response.json() if action.get('type') == 'commentCard']
        return comments[:limit]

    def save_initial_comment_date(self, card_id):
        last_comment = self.get_card_comments(card_id)[0]
        utils.save_value('last_comment_date', last_comment.get('date'))

    def fetch_new_comments(self, board_name, card_name):
        card = self.get_card_on_board_by_name(board_name, card_name)
        comments = self.get_card_comments(card.get('id'))

        last_comment_date = dt.strptime(utils.load_value('last_comment_date'), '%Y-%m-%dT%H:%M:%S.%fZ')
        new_comments = [
            comment for comment in comments if
            dt.strptime(comment.get('date'), '%Y-%m-%dT%H:%M:%S.%fZ') > last_comment_date
        ]
        return new_comments



# api_key = settings.TRELLO_API_KEY
# api_token = settings.TRELLO_API_TOKEN
# board_name = settings.TRELLO_BOARD_NAME
# card_name = settings.TRELLO_CARD_NAME

# trello_api = TrelloAPI(api_key, api_token)
# card_id = trello_api.get_card_on_board_by_name(board_name, card_name).get('id')
# print(card_id)
# print(trello_api.get_card_comments(card_id))

# trello_api.save_initial_comment_date(card_id)
# print(trello_api.fetch_new_comments(board_name, card_name))
