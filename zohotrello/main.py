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

new_comments = TrelloAPI.fetch_new_comments(settings.TRELLO_BOARD_NAME, settings.TRELLO_CARD_NAME)
for comment in new_comments:
    comment_text = comment.get('data').get('text')
    pprint(comment_text)
    # print(utils.is_exchange(comment_text))
    # print(utils.extract_comment_entities(comment_text))
