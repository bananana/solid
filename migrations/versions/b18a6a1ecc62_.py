"""empty message

Revision ID: b18a6a1ecc62
Revises: c6f5a4b7a379
Create Date: 2018-05-25 13:45:09.317898

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b18a6a1ecc62'
down_revision = 'c6f5a4b7a379'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('likes',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('log_item_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['log_item_id'], ['log_events.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users_user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('likes')
    # ### end Alembic commands ###