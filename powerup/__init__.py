import os
from tokenize import Token
from flask import Flask, Response, request
from .database import (
    db_session,
    init_db
)
from .models.webhook_payload import WebhookPayloadModel
from .models.board_webhook import BoardWebhookModel
from .trello_helpers import post_comment, get_member_boards, get_board_trello, register_board_webhook

KEY             = os.environ["KEY"]
TOKEN           = os.environ["TOKEN"]
CALLBACK_URL    = os.environ["CALLBACK_URL"]
ENV             = os.environ.get("ENV")

def create_app():
    app = Flask(__name__)

    @app.before_first_request
    def create_tables():
        """Create tables and upsert seed mutation_type"""
        init_db()


    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """
        Flask will automatically remove database sessions at the end of the request or 
        when the application shuts down.
        """
        db_session.remove()


    @app.route("/powerup/ping/")
    def pong():
        return {"status": "success",
              "data": {
                  "message": "pong"
              }}, 200

    @app.get("/powerup/webhook/")
    def webhook_head():
        return Response(status=200)

    @app.post("/powerup/webhook/")
    def webhook_post():
        action_payload = request.get_json().get("action")
        action_type    = action_payload.get("type")

        if "label" not in action_type.lower():
            return Response(status=200)

        webhook_payload = WebhookPayloadModel(action_type=action_type, action_payload=action_payload)
        if webhook_payload.card_id is None:
            status_code = 200
        else:
            _, status_code = post_comment(comment= webhook_payload.comment, card_id= webhook_payload.card_id, KEY=KEY, TOKEN=TOKEN)
        
        if status_code == 200:
            webhook_payload.status = "Success"
        else:
            webhook_payload.status = "Fail"
        db_session.add(webhook_payload)
        db_session.commit()
        return Response(status=200)

    @app.get("/powerup/board/")
    def get_all_board():
        board_data, status_code = get_member_boards(KEY=KEY, TOKEN=TOKEN)
        if status_code == 200:
            return {"status": "Success",
                    "data" : board_data}, status_code
        else:
            return {"status": "Fail",
                    "data" : None}, status_code

    @app.get("/powerup/board/<board_id>")
    def get_board(board_id):
        board_data = BoardWebhookModel.query.filter(BoardWebhookModel.id == board_id).first()
        if board_data:
            status_code = 200
        else:
            board_data = None
            status_code = 404

        if status_code == 200:
            return {"status": "Success",
                    "data" : board_data}, status_code
        else:
            return {"status": "Fail",
                    "data" : None}, status_code

    @app.post("/powerup/board/<board_id>")
    def post_board_webhook(board_id):
        board_data = BoardWebhookModel.query.filter(BoardWebhookModel.id == board_id).first()
        if board_data:
            if board_data.webhook_active:
                return {"status": "Success",
                        "data" : board_data,
                        "message": "Board already have webhook"}, 200
        
        board_data, status_code = get_board_trello(board_id=board_id, KEY=KEY, TOKEN=TOKEN)
        if status_code != 200:
            return {"status": "Fail",
                    "data" : None,
                    "message": f"failed get board {board_id=!r} from trello"}, status_code
        board_data["_id"] = board_data.pop("id")
        board = BoardWebhookModel(**board_data)

        webhook_data, status_code = register_board_webhook(ENV=ENV, board_id=board_id, callbackURL= CALLBACK_URL,KEY= KEY, TOKEN=TOKEN, board_name=board.name)
        if status_code == 200:
            board.webhook_id        = webhook_data.get("id")
            board.webhook_active    = webhook_data.get("active", False)
            db_session.add(board)
            db_session.commit()

            return {"status": "Success",
                    "data" : board.json(),
                    "message": f"Webhook created for board {board.name!r}!"}, status_code
        
        return {"status": "Fail",
                "data" : webhook_data,
                "message": f"Failed webhook_creation for {board_id=!r}"}, status_code




    return app