from app import db, app
from app.mixins import CRUDMixin

from sqlalchemy_i18n import Translatable, translation_base


class Page(CRUDMixin, db.Model, Translatable):
    __tablename__ = 'pages_page'

    __translatable__ = {
        'locales': app.config['SUPPORTED_LANGUAGES']
    }

    id = db.Column(db.Integer, primary_key=True)

    url = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<Page %r>' % (self.name)


class PageTranslation(translation_base(Page)):
    __tablename__ = 'pages_page_translation'

    name = db.Column(db.String(128))
    content = db.Column(db.Text)

    def __repr__(self):
        return '<Page %r>' % (self.name)
