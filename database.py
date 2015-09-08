import arrow
import uuid

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy import exc

db = SQLAlchemy()
migrate = Migrate()


def get_current_datetime():
    return arrow.now().datetime


def generate_uuid():
    an_id = str(uuid.uuid4())
    print("id created is: " + an_id)
    return an_id


class Model:

    """Base class for models with CRUD operations."""

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.String(), nullable=False, default=generate_uuid, primary_key=True)
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
            except exc.SQLAlchemyError:
                db.session.rollback()
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


class ChessGame(Model, db.Model):

    __tablename__ = 'chess_game'

    password1 = db.Column(db.String())
    password2 = db.Column(db.String())
    board = db.Column(JSONB)
    move_history = db.Column(JSONB)
