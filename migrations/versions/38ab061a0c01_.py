"""empty message

Revision ID: 38ab061a0c01
Revises: 1944900d3b2c
Create Date: 2017-08-30 13:07:41.899011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38ab061a0c01'
down_revision = '1944900d3b2c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('causes_action_comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('action_id', sa.Integer(), nullable=True),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['action_id'], ['causes_action.id'], ),
    sa.ForeignKeyConstraint(['author_id'], ['users_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('causes_action_comment')
    # ### end Alembic commands ###
