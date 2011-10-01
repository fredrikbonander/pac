class FormValidationError(Exception):
    def __init__(self, *args, **kwargs):
        super(FormValidationError, self).__init__(*args, **kwargs)
        # *args is used to get a list of the parameters passed in
        self.args = [a for a in args]


def validate_username(username):
    if len(username) < 6:
        raise FormValidationError(-10, 'Username is too short')


def validate_password(password, password2):
    if len(password) < 6:
        raise FormValidationError(-11, 'Password is too short')

    if password != password2:
        raise FormValidationError(-12, 'Password miss match')

  