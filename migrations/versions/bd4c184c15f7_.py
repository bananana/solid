"""empty message

Revision ID: bd4c184c15f7
Revises: f8c51b97cb4a
Create Date: 2018-03-29 01:11:09.079023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd4c184c15f7'
down_revision = 'f8c51b97cb4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('discussions_post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('discussions_post', schema=None) as batch_op:
        batch_op.drop_column('deleted')

    # ### end Alembic commands ###