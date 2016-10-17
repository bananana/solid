from app import db
from app.mixins import CRUDMixin


class Page(CRUDMixin, db.Model):
    __tablename__ = 'pages_page'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(128), nullable=False)
    url           = db.Column(db.String(128), nullable=False)
    content       = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Page %r>' % (self.name)
