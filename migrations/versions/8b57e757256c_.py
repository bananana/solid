"""empty message

Revision ID: 8b57e757256c
Revises: f4984bdb99ec
Create Date: 2017-04-18 13:15:10.426348

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b57e757256c'
down_revision = 'f4984bdb99ec'
branch_labels = None
depends_on = None

Action = sa.sql.table('causes_action',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('_title', sa.String(length=128)),
    sa.sql.column('_summary', sa.Text()),
    sa.sql.column('_description', sa.Text())
)

ActionTranslation = sa.sql.table('causes_action_translation',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('title', sa.String(length=128)),
    sa.sql.column('summary', sa.Text()),
    sa.sql.column('description', sa.Text()),
    sa.sql.column('locale', sa.String(length=10)),
)


def upgrade():
    conn = op.get_bind()

    results = conn.execute(sa.select([Action]))

    actions = []

    for _id, title, summary, description in results:
        actions.append({
            'id': _id,
            'title': title,
            'summary': summary,
            'description': description,
            'locale': 'en',
        })

    op.bulk_insert(ActionTranslation, actions)


def downgrade():
    conn = op.get_bind()

    results = conn.execute(sa.select([ActionTranslation]))

    causes = []

    for _id, title, intro, summary, description in results:
        op.execute(
            Action.update().where(
                Action.c.id == _id
            ).values(
                _title=title,
                _summary=summary,
                _description=description,
            )
        )
