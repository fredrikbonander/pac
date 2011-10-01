import unittest
from pac.setup import validate_form, FormValidationError

class TestFormValidationHandler(unittest.TestCase):
    def test_to_short_username(self):
        form = dict(username='fre', password='12', password2='13')
        status = dict(status_code=1, message='')

        try:
            validate_form(form)
        except FormValidationError, e:
            status['status_code'] = e.args[0]
            status['status_message'] = e.args[1]

        self.assertEqual(status['status_code'], -10)

    def test_to_short_password(self):
        form = dict(username='fredrik', password='12', password2='13')
        status = dict(status_code=1, message='')

        try:
            validate_form(form)
        except FormValidationError, e:
            status['status_code'] = e.args[0]
            status['status_message'] = e.args[1]

        self.assertEqual(status['status_code'], -11)

    def test_miss_matched_passwords(self):
        form = dict(username='fredrik', password='123456', password2='123457')
        status = dict(status_code=1, message='')

        try:
            validate_form(form)
        except FormValidationError, e:
            status['status_code'] = e.args[0]
            status['status_message'] = e.args[1]

        self.assertEqual(status['status_code'], -12)


    def test_valid_form(self):
        form = dict(username='fredrik', password='123456', password2='123456')
        status = dict(status_code=1, message='')

        try:
            validate_form(form)
        except FormValidationError, e:
            status['status_code'] = e.args[0]
            status['status_message'] = e.args[1]

        self.assertEqual(status['status_code'], 1)
