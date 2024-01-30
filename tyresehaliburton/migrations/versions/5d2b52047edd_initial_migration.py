"""Initial migration.

Revision ID: 5d2b52047edd
Revises: 9f6648b8b230
Create Date: 2024-01-29 20:04:17.510169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d2b52047edd'
down_revision = '9f6648b8b230'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('assist_leader',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('player_name', sa.String(), nullable=False),
    sa.Column('assists', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('player_id')
    )
    op.create_table('game_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('game_date', sa.DateTime(), nullable=False),
    sa.Column('assists', sa.Integer(), nullable=False),
    sa.Column('turnovers', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('game_log')
    op.drop_table('assist_leader')
    # ### end Alembic commands ###
