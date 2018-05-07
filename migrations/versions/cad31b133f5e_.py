"""copy Cause content to CauseTranslation

Revision ID: cad31b133f5e
Revises: 2d56302e6e24
Create Date: 2017-04-18 00:41:35.359993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cad31b133f5e'
down_revision = '2d56302e6e24'
branch_labels = None
depends_on = None


Cause = sa.sql.table('causes_cause',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('_title', sa.String(length=40)),
    sa.sql.column('_intro', sa.String(length=40)),
    sa.sql.column('_story_heading', sa.String(length=128)),
    sa.sql.column('_story_content', sa.Text())
)

CauseTranslation = sa.sql.table('causes_cause_translation',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('title', sa.String(length=40)),
    sa.sql.column('intro', sa.String(length=40)),
    sa.sql.column('story_heading', sa.String(length=128)),
    sa.sql.column('story_content', sa.Text()),
    sa.sql.column('locale', sa.String(length=10)),
)


def upgrade():
    conn = op.get_bind()

    results = conn.execute(sa.select([Cause]))

    causes = []

    for _id, title, intro, story_heading, story_content in results:
        causes.append({
            'id': _id,
            'title': title,
            'intro': intro,
            'story_heading': story_heading,
            'story_content': story_content,
            'locale': 'en',
        })

    op.bulk_insert(CauseTranslation, causes)


def downgrade():
    conn = op.get_bind()

    results = conn.execute(sa.select([CauseTranslation]))

    causes = []

    for _id, title, intro, story_heading, story_content, locale in results:
        op.execute(
            Cause.update().where(
                Cause.c.id == _id
            ).values(
                _title=title,
                _intro=intro,
                _story_heading=story_heading,
                _story_content=story_content,
            )
        )
