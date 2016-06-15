"""Associate players to games.

Revision ID: 555f67c78d9
Revises: 6dd5917904
Create Date: 2015-12-31 23:38:24.550083

"""

# revision identifiers, used by Alembic.
revision = '555f67c78d9'
down_revision = '6dd5917904'

from alembic import op


def upgrade():
    op.create_foreign_key(None, 'games', 'users', ['player_2_id'], ['id'])
    op.create_foreign_key(None, 'games', 'users', ['player_1_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'games', type_='foreignkey')
    op.drop_constraint(None, 'games', type_='foreignkey')
