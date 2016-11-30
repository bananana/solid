from sqlalchemy_i18n import Translatable
from sqlalchemy_i18n import translation_base

from app import db, app
from app.mixins import CRUDMixin


class Page(Translatable, CRUDMixin, db.Model):
    __tablename__ = 'pages_page'

    __translatable__ = {
        'locales': app.config['SUPPORTED_LANGUAGES']
    }

    id            = db.Column(db.Integer, primary_key=True)
    url           = db.Column(db.String(128), nullable=False)

    locale        = app.config['BABEL_DEFAULT_LOCALE']

    def __repr__(self):
        return '<Page %r>' % (self.name)


class PageTranslation(translation_base(Page)):
    __tablename__ = 'pages_page_i18n'
    name          = db.Column(db.String(128), nullable=False)
    content       = db.Column(db.Text, nullable=False)
