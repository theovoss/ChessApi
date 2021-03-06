"""Create initial chess game table.

Revision ID: 1fda5450aaa
Revises: None
Create Date: 2015-09-19 12:36:55.725071

"""

# revision identifiers, used by Alembic.
revision = '1fda5450aaa'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('chess_game',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('archived', sa.Integer(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('password1', sa.String(), nullable=True),
                    sa.Column('password2', sa.String(), nullable=True),
                    sa.Column('board', postgresql.JSONB(), nullable=True),
                    sa.Column('move_history', postgresql.JSONB(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('chess_game')
