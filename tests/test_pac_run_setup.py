import webapp2
from webapp2_extras.appengine.auth.models import User
from ndb import model
from tests import test_utils

import config
import routes

from pac import setup as pac_setup

app = webapp2.WSGIApplication(config=config.webapp2_config)
routes.add_routes(app)

class TestSetupHandler(test_utils.DatastoreTest):
    def test_check_if_setup_can_be_run(self):
        setup_status = pac_setup.is_setup_complete()

        self.assertEqual(setup_status, False)

    def test_setup_to_complete(self):
        class dbSettings(model.Model):
            value = model.StringProperty(required=True)

        pac_setup.set_setup_to_complete()

        setup_status = pac_setup.is_setup_complete()

        self.assertEqual(setup_status, True)

    def test_create_new_user_form_setup(self):
        self.register_model('User', User)

        req = webapp2.Request.blank('/edit/setup/',
                                    POST={'username': 'administrator', 'password': 'qwerty', 'password2': 'qwerty'},
                                    headers=[('Content-Type', 'application/x-www-form-urlencoded; charset=utf-8')])
        req.app = app
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 302)

        rsp = app.get_response('/edit/login/', POST={'username': 'administrator', 'password': 'qwerty'},
                               headers=[('Content-Type', 'application/x-www-form-urlencoded; charset=utf-8')])
        self.assertEqual(rsp.status_int, 302)
