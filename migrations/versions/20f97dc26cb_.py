"""Add player ids.

Revision ID: 20f97dc26cb
Revises: 28f98ca9634
Create Date: 2015-12-07 21:58:15.798743

"""

# revision identifiers, used by Alembic.
revision = '20f97dc26cb'
down_revision = '28f98ca9634'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('games', sa.Column('player_1_id', postgresql.UUID(), nullable=False))
    op.add_column('games', sa.Column('player_2_id', postgresql.UUID(), nullable=True))


def downgrade():
    op.drop_column('games', 'player_2_id')
    op.drop_column('games', 'player_1_id')
