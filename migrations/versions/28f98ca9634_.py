"""Create initial users and games tables.

Revision ID: 28f98ca9634
Revises: 1fda5450aaa
Create Date: 2015-10-25 15:45:05.714615

"""

# revision identifiers, used by Alembic.
revision = '28f98ca9634'
down_revision = '1fda5450aaa'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('games',
                    sa.Column('id', postgresql.UUID(), nullable=False),
                    sa.Column('archived', sa.Integer(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('board', postgresql.JSONB(), nullable=True),
                    sa.Column('move_history', postgresql.JSONB(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('users',
                    sa.Column('id', postgresql.UUID(), nullable=False),
                    sa.Column('archived', sa.Integer(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('password', sa.String(), nullable=True),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('email', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )
    op.create_table('user_games',
                    sa.Column('user_id', postgresql.UUID(), nullable=True),
                    sa.Column('game_id', postgresql.UUID(), nullable=True),
                    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
                    )
    op.drop_table('chess_game')


def downgrade():
    op.create_table('chess_game',
                    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('archived', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
                    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
                    sa.Column('password1', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('password2', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('board', postgresql.JSONB(), autoincrement=False, nullable=True),
                    sa.Column('move_history', postgresql.JSONB(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='chess_game_pkey')
                    )
    op.drop_table('user_games')
    op.drop_table('users')
    op.drop_table('games')
