"""empty message

Revision ID: d568eda603db
Revises: 3de620b399d7
Create Date: 2017-04-18 13:09:41.748376

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd568eda603db'
down_revision = '3de620b399d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('migrate_version')
    op.drop_table('migration_tmp')
    with op.batch_alter_table('causes_action', schema=None) as batch_op:
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)

    with op.batch_alter_table('causes_cause', schema=None) as batch_op:
        batch_op.alter_column('slug',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)

    with op.batch_alter_table('discussions_post', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)

    with op.batch_alter_table('log_event_types', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['name'])

    with op.batch_alter_table('log_events', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'users_user', ['user_id'], ['id'])
        batch_op.create_foreign_key(None, 'log_event_types', ['event_type_id'], ['id'])

    with op.batch_alter_table('pages_page', schema=None) as batch_op:
        batch_op.alter_column('content',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
        batch_op.alter_column('url',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)

    with op.batch_alter_table('users_user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_user_email'), ['email'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_user_employer'), ['employer'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_user_phone'), ['phone'], unique=False)
        batch_op.create_unique_constraint(None, ['social_id'])
        batch_op.drop_column('private_full_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users_user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('private_full_name', sa.BOOLEAN(), nullable=True))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_index(batch_op.f('ix_users_user_phone'))
        batch_op.drop_index(batch_op.f('ix_users_user_employer'))
        batch_op.drop_index(batch_op.f('ix_users_user_email'))

    with op.batch_alter_table('pages_page', schema=None) as batch_op:
        batch_op.alter_column('url',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
        batch_op.alter_column('content',
               existing_type=sa.TEXT(),
               nullable=True)

    with op.batch_alter_table('log_events', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('log_event_types', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('discussions_post', schema=None) as batch_op:
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
        batch_op.alter_column('body',
               existing_type=sa.TEXT(),
               nullable=True)

    with op.batch_alter_table('causes_cause', schema=None) as batch_op:
        batch_op.alter_column('slug',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)

    with op.batch_alter_table('causes_action', schema=None) as batch_op:
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)

    op.create_table('migration_tmp',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('social_id', sa.VARCHAR(length=64), nullable=True),
    sa.Column('is_admin', sa.BOOLEAN(), nullable=True),
    sa.Column('last_login', sa.DATETIME(), nullable=True),
    sa.Column('nickname', sa.VARCHAR(length=64), nullable=True),
    sa.Column('password', sa.VARCHAR(length=128), nullable=True),
    sa.Column('full_name', sa.VARCHAR(length=64), nullable=True),
    sa.Column('initials', sa.VARCHAR(length=8), nullable=True),
    sa.Column('color', sa.VARCHAR(length=7), nullable=True),
    sa.Column('email', sa.VARCHAR(length=128), nullable=True),
    sa.Column('phone', sa.INTEGER(), nullable=True),
    sa.Column('employer', sa.VARCHAR(length=64), nullable=True),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('private_full_name', sa.BOOLEAN(), nullable=True),
    sa.Column('zip', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('migrate_version',
    sa.Column('repository_id', sa.VARCHAR(length=250), nullable=False),
    sa.Column('repository_path', sa.TEXT(), nullable=True),
    sa.Column('version', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('repository_id')
    )
    # ### end Alembic commands ###