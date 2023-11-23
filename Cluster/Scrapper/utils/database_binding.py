from typing import List
import os
from typing import Optional
from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session

from sqlalchemy import create_engine


class Stats(DeclarativeBase):
    __tablename__ = "chat_data"
    __table_args__ = {'extend_existing': True}

    message_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    time_uploaded: Mapped[datetime] = mapped_column(DateTime)
    username: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer)
    reply_to_msg_id: Mapped[Optional[int]] = mapped_column(Integer)
    reactions: Mapped[Optional[str]] = mapped_column(String)
    text: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"Stats(" \
               f"message_id={self.message_id!r}, " \
               f"time_uploaded={self.time_uploaded!r}, " \
               f"user_id={self.user_id!r} " \
               f"reply_to_msg_id={self.reply_to_msg_id!r} " \
               f"reactions={self.reactions!r} " \
               f"text={self.text} " \
               f")"


class DataBaseBinding:
    def __init__(self, database: str):
        self.user = os.getenv('POSTGRES_USER')
        self.password = os.getenv('POSTGRES_PASSWORD')
        self.host = os.getenv('POSTGRES_HOST')
        self.port = os.getenv('POSTGRES_PORTS')
        self.db = database
        self.engine = create_engine(f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}')

    def create_tables(self):
        DeclarativeBase.metadata.create_all(self.engine)

    def insert_data(self, data_dict: dict):
        with Session(self.engine) as session:
            message = Stats(message_id=data_dict['message_id'],
                          time_uploaded=data_dict['time_uploaded'],
                          user_id=data_dict['user_id'],
                          username=data_dict['username'],
                          reply_to_msg_id=data_dict['reply_to_msg_id'],
                          reactions=data_dict['reply_to_msg_id'],
                          text=data_dict['text']
                          )
            session.add(message)
            session.commit()
