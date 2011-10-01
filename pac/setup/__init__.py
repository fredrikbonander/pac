from pac.form_utils import FormValidationError
from pac.form_utils import validate_username
from pac.form_utils import validate_password
from pac.settings.models import dbSettings

def get_setup_entry():
    return dbSettings.get_by_id('setup_status')

def is_setup_complete():
    setup_setting = get_setup_entry()

    if setup_setting and setup_setting.value == 'complete':
        return True

    return False

def set_setup_to_complete():
    return dbSettings.get_or_insert('setup_status', value='complete')

def validate_form(form):
    validate_username(form.get('username'))
    validate_password(form.get('password'), form.get('password2'))

def add_new_admin_user(auth, form, status):
    try:
        validate_form(form)
        user = auth.store.user_model.create_user(form.get('username'), password_raw=form.get('password'))
        if not user[0]: #user is a tuple
            status['status_code'] = -1
            status['status_message'] = user[1] # Error message

    except FormValidationError, e:
        status['status_code'] = e.args[0]
        status['status_message'] = e.args[1]
