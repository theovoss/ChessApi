import factory
import uuid
from chess import chess

from factory.alchemy import SQLAlchemyModelFactory
from api.database import db, Game, User
from factory import fuzzy

default_chess_board = chess.ChessBoard().export()


def get_uuid():
    return factory.LazyAttribute(lambda n: uuid.uuid4())


def get_random_string():
    return fuzzy.FuzzyText()


class BaseFactory(SQLAlchemyModelFactory):
    id = get_uuid()
    archived = 0

    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class GameFactory(BaseFactory):
    board = default_chess_board
    move_history = {}

    # @factory.post_generation
    # def _players(self, create, extracted, **kwargs):
    #     self.players = [UserFactory, UserFactory]

    class Meta:
        model = Game


class UserFactory(BaseFactory):
    password = get_random_string()
    email = get_random_string()
    name = get_random_string()

    class Meta:
        model = User
