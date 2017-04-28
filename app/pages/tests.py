from flask import url_for
from flask_login import current_user

from app import app

from app.tests_base import BaseTestCase
from app.pages.models import Page


class PostViewsTests(BaseTestCase):
    #: Enable testing mode
    app.config['TESTING'] = True

    #: Do not render templates, we're only testing logic here.
    render_templates = False

    test_page = {
        "name": "Test",
        "url": "/test",
        "content": "test"
    }

    def test_page_create(self):
        pass

    def test_page_view(self):
        p = Page.create(**self.test_page)
        with self.client as client: 
            response = client.get(self.test_page['url'])
            self.assert_context('page', p)
            self.assert_200(response)
