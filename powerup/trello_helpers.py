from datetime import (
    datetime, 
    timedelta,
    timezone, 
)
import requests

def generate_datetime(_id: str):
    """generate utc+7 datetime from id"""
    if _id:
        return datetime.fromtimestamp(int(_id[0:8], 16), timezone(timedelta(hours=7)))
    return None

def post_comment(comment: str, card_id: str, KEY:str, TOKEN:str):
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
    params = {
        "text"  : comment,
        "key"   : KEY,
        "token" : TOKEN,
    }
    response = requests.post(url, params=params)
    # response.raise_for_status()
    return response.json(), response.status_code

def get_member_boards(KEY:str, TOKEN:str, fields: list = ["name", "id", "url"]):
    url = f"https://api.trello.com/1/members/me/boards"
    params = {
        "key"   : KEY,
        "token" : TOKEN,
        "fields": fields,
    }
    response = requests.get(url, params=params)
    # response.raise_for_status()
    return response.json(), response.status_code

def get_board_trello(board_id, KEY:str, TOKEN:str, fields: list = ["name", "id", "url"]):
    url = f"https://api.trello.com/1/boards/{board_id}"
    params = {
        "key"   : KEY,
        "token" : TOKEN,
        "fields": fields,
    }
    response = requests.get(url, params=params)
    # response.raise_for_status()
    return response.json(), response.status_code

def register_board_webhook(ENV, board_id, KEY:str, callbackURL: str, TOKEN:str, board_name=""):
    if ENV=="development":
        return {"id": "development", "active": False}, 200
    
    url = f"https://api.trello.com/1/webhooks"
    params = {
        "key"   : KEY,
        "token" : TOKEN,
        "idModel": board_id,
        "callbackURL": callbackURL,
        "description": f"Created from trello-label-powerup to monitor labels changes on {board_name=!r}."
    }
    response = requests.post(url, params=params)
    # response.raise_for_status()
    return response.json(), response.status_code