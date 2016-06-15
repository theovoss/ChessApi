"""Remove user_game association table.

Revision ID: 6dd5917904
Revises: 20f97dc26cb
Create Date: 2015-12-25 17:56:39.262063

"""

# revision identifiers, used by Alembic.
revision = '6dd5917904'
down_revision = '20f97dc26cb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.drop_table('user_games')


def downgrade():
    op.create_table('user_games',
                    sa.Column('user_id', postgresql.UUID(), autoincrement=False, nullable=True),
                    sa.Column('game_id', postgresql.UUID(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['game_id'], ['games.id'], name='user_games_game_id_fkey'),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_games_user_id_fkey')
                    )
