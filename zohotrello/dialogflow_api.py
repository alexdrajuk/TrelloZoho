from google.protobuf.json_format import MessageToDict
import dialogflow_v2 as dialogflow

from zohotrello import settings


def detect_intent_text(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    response_content = MessageToDict(response.query_result)
    return {
        'expense_account': response_content.get('fulfillmentMessages')[0].get('payload').get('expense_account'),
        'params': response_content.get('parameters'),
        'query_text': response_content.get('queryText')
    }
