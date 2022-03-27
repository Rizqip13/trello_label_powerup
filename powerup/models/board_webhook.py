from sqlalchemy import (
    Boolean,
    Column,
    String, 
    Text, 
)

from ..database import Base

class BoardWebhookModel(Base):
    __tablename__ = "board_webhook"

    id                          = Column(String(24), primary_key=True) 
    name                        = Column(Text(), nullable=False)
    url                         = Column(Text(), nullable=False)
    webhook_id                  = Column(String(24), nullable=True)
    webhook_active              = Column(Boolean, default=False)

    def __init__(self, _id: str, name: str, url: str, webhook_id: str=None, webhook_active: bool=False):
        """_id is always created by trello"""
        self.id                         = _id
        self.name                       = name
        self.url                        = url
        self.webhook_id                 = webhook_id
        self.webhook_active             = webhook_active
        
    def __repr__(self):
        return f"<Board(name={self.name!r}, id={self.id!r})>"

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "webhook_id": self.webhook_id,
            "webhook_active": self.webhook_active
        }