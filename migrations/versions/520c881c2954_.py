"""empty message

Revision ID: 520c881c2954
Revises: 01e9c4fc3ac4
Create Date: 2017-04-18 01:51:49.318550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '520c881c2954'
down_revision = '01e9c4fc3ac4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('causes_cause', schema=None) as batch_op:
        batch_op.drop_column('_intro')
        batch_op.drop_column('_title')
        batch_op.drop_column('_story_content')
        batch_op.drop_column('_story_heading')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('causes_cause', schema=None) as batch_op:
        batch_op.add_column(sa.Column('_story_heading', sa.VARCHAR(length=128), nullable=True))
        batch_op.add_column(sa.Column('_story_content', sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column('_title', sa.VARCHAR(length=128), nullable=False))
        batch_op.add_column(sa.Column('_intro', sa.TEXT(), nullable=True))

    # ### end Alembic commands ###