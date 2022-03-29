from datetime import (
    datetime, 
    timedelta,
    timezone, 
)

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    Text
)

from ..database import (
    Base,
)
from ..trello_helpers import generate_datetime

class WebhookPayloadModel(Base):
    """
    status start from "received" then change to either "successful" or "error"
    """
    __tablename__ = "webhook_payload"

    id              = Column(Integer, primary_key=True)
    action_id       = Column(String(24))
    action_at       = Column(DateTime())
    action_type     = Column(String(128))
    board_id        = Column(String(24))
    board_name      = Column(Text())
    card_id         = Column(String(24), nullable=True)
    card_shortLink  = Column(String(8), nullable=True)
    card_name       = Column(Text(), nullable=True)
    label_id        = Column(String(24))
    label_name      = Column(String(512))
    label_color     = Column(String(512))
    actor_fullname  = Column(String(512))
    actor_username  = Column(String(512))
    actor_member_id = Column(String(24))
    payload         = Column(JSON)
    received_at     = Column(DateTime, default=lambda : datetime.now(tz=timezone(timedelta(hours=7))))
    status          = Column(String(24))

    comment         = Column(Text())

    def __init__(self, action_type, action_payload):
        self.action_id         = action_payload.get("id")
        self.action_type       = action_type
        self.action_at         = generate_datetime(self.action_id)
        self.board_id          = action_payload.get("data", {}).get("board", {}).get("id")
        self.board_name        = action_payload.get("data", {}).get("board", {}).get("name")
        self.card_id           = action_payload.get("data", {}).get("card", {}).get("id")
        self.card_shortLink    = action_payload.get("data", {}).get("card", {}).get("shortLink")
        self.card_name         = action_payload.get("data", {}).get("card", {}).get("name")
        self.label_id          = action_payload.get("data", {}).get("label", {}).get("id")
        self.label_name        = action_payload.get("data", {}).get("label", {}).get("name")
        self.label_color       = action_payload.get("data", {}).get("label", {}).get("color")
        self.actor_fullname    = action_payload.get("memberCreator", {}).get("fullName")
        self.actor_username    = action_payload.get("memberCreator", {}).get("username")
        self.actor_member_id   = action_payload.get("memberCreator", {}).get("id")
        self.payload           = action_payload

        self.comment           = f"{self.actor_fullname} - {self.actor_username} : {self.action_type} label [{self.label_color}] {self.label_name!r} at {self.action_at}"


    def __repr__(self):
        return f"<WebhookPayload(action_id={self.action_id!r}, board_id={self.board_id!r}, status={self.status!r})>"