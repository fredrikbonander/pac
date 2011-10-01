from ndb import model
import webapp2
from tests import test_utils

from pac import pages
from pac.pages.model import dbPages
from pac.pages.model import dbPageModules

import config
import routes

app = webapp2.WSGIApplication(config=config.webapp2_config)
routes.add_routes(app)

class FredTests(test_utils.DatastoreTest):
    def test_1(self):
        class Ent1(model.Model):
          name = model.StringProperty()
        class Ent2(model.Model):
          age = model.StringProperty()

        ent = Ent1(name='fredrik')
        key = ent.put()

        ent2 = Ent2(parent=key, age='12')
        ent2.put()

        test_ent = Ent2.query(ancestor=key).get()
        self.assertEqual(test_ent.age, '12')


class TestPagesHandler(test_utils.DatastoreTest):
    def test_create_a_new_page(self):
        self.register_model('dbPages', dbPages)

        form_data = dict(page_name='First page')
        status = dict()

        page = pages.insert_or_update_page(form_data, status)

        new_page = page.get()

        self.assertEqual(new_page.name, 'First page')

    def test_create_a_new_page_with_content(self):
        self.register_model('dbPages', dbPages)
        self.register_model('dbPageModules', dbPageModules)

        form_data = {'page_name': 'First page', 'content_module|MainHeading': 'Some title'}
        status = dict()

        page = pages.insert_or_update_page(form_data, status)

        new_page = page.get()

        self.assertEqual(new_page.name, 'First page')
        self.assertEqual(new_page.page_modules['MainHeading'], 'Some title')