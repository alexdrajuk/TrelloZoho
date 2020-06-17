import requests

import settings


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
        response = requests.get(url, headers=headers, params=query)
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
        response = requests.get(url, headers=headers, params=query)
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
        response = requests.get(url, headers=headers, params=query)
        response.raise_for_status()
        cards = [card for card in response.json() if card.get('type') == 'commentCard']
        return cards[limit:]
