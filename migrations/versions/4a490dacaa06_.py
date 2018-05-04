"""copy Page data to PageTranslation

Revision ID: 4a490dacaa06
Revises: f992c0df5662
Create Date: 2017-04-18 17:02:28.251211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a490dacaa06'
down_revision = 'f992c0df5662'
branch_labels = None
depends_on = None


Page = sa.sql.table('pages_page',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('_name', sa.String(length=40)),
    sa.sql.column('_content', sa.Text())
)

PageTranslation = sa.sql.table('pages_page_translation',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('name', sa.String(length=40)),
    sa.sql.column('content', sa.Text()),
    sa.sql.column('locale', sa.String(length=10)),
)


def upgrade():
    conn = op.get_bind()

    results = conn.execute(sa.select([Page]))

    pages = []

    for _id, name, content in results:
        pages.append({
            'id': _id,
            'name': name,
            'content': content,
            'locale': 'en',
        })

    op.bulk_insert(PageTranslation, pages)


def downgrade():
    conn = op.get_bind()

    results = conn.execute(sa.select([PageTranslation]))

    pages = []

    for _id, name, content, locale in results:
        op.execute(
            Page.update().where(
                Page.c.id == _id
            ).values(
                _name=name,
                _content=content,
            )
        )
