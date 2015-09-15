import factory
import uuid
from chess import chess

from factory.alchemy import SQLAlchemyModelFactory
from api.database import db, ChessGame
from factory import fuzzy

default_chess_board = chess.ChessBoard().export()


def get_uuid():
    return factory.LazyAttribute(lambda n: str(uuid.uuid4()))


def get_random_string():
    return fuzzy.FuzzyText()


class BaseFactory(SQLAlchemyModelFactory):
    id = get_uuid()
    archived = 0

    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class ChessGameFactory(BaseFactory):
    password1 = get_random_string()
    password2 = None
    board = default_chess_board
    move_history = {}

    class Meta:
        model = ChessGame
