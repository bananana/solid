"""add User.locale

Revision ID: 3de620b399d7
Revises: 520c881c2954
Create Date: 2017-04-18 10:13:33.482416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3de620b399d7'
down_revision = '520c881c2954'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users_user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('locale', sa.String(length=2), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users_user', schema=None) as batch_op:
        batch_op.drop_column('locale')

    # ### end Alembic commands ###
