from app import db
from app.mixins import CRUDMixin


class Page(CRUDMixin, db.Model):
    __tablename__ = 'pages_page'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(128))
    url           = db.Column(db.String(128))
    content       = db.Column(db.Text)

    def __repr__(self):
        return '<Page %r>' % (self.name)
