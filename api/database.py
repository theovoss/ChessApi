from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy import exc

from .utilities import get_current_datetime, generate_uuid

db = SQLAlchemy()
migrate = Migrate()


class Model:

    """Base class for models with CRUD operations."""

    __table_args__ = {'extend_existing': True}

    id = db.Column(UUID(as_uuid=True), nullable=False, default=generate_uuid, primary_key=True)
    archived = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=get_current_datetime)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=get_current_datetime)

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        my_id = generate_uuid()
        instance = cls(id=my_id, **kwargs)
        instance.created_at = get_current_datetime()
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            if value is not None:
                setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        self.updated_at = get_current_datetime()
        db.session.add(self)
        if commit:
            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                print("rolling back")
                print("exception is:")
                print(e)
                db.session.rollback()
        else:
            print("didn't commit")
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        self.archived = 1
        self.updated_at = get_current_datetime()
        return commit and db.session.commit()

    def to_obj(self):
        ret_val = {}
        for column in self.__table__.c:
            ret_val[str(column.key)] = getattr(self, column.key)
        return ret_val


class Game(Model, db.Model):

    __tablename__ = 'games'

    board = db.Column(JSONB)
    move_history = db.Column(JSONB)
    player_1_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    player_2_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))

    player_1 = db.relationship("User", foreign_keys="Game.player_1_id")
    player_2 = db.relationship("User", foreign_keys="Game.player_2_id")

    @property
    def current_player(self):
        if self.board['players']['current'] == "Player 1":
            return self.player_1
        else:
            return self.player_2

    @property
    def players(self):
        return [self.player_1, self.player_2]

    @players.setter
    def players(self, value):
        if isinstance(value, list):
            if len(value) > 1:
                if not self.player_1_id:
                    self.player_1_id = value[0].id
                if not self.player_2_id:
                    self.player_2_id = value[1].id
            else:
                if not self.player_1_id:
                    self.player_1_id = value[0].id

    @property
    def is_full(self):
        if len(self.players) == len(self.board['players']):
            return True
        return False


class User(Model, db.Model):

    __tablename__ = 'users'

    password = db.Column(db.String())
    name = db.Column(db.String())
    email = db.Column(db.String(), unique=True)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        print("id is: {}".format(self.id))
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def valid_password(self, password):
        if password == self.password:
            return True
        return False
