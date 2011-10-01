from pac.handlers import BaseHandler
from pac.setup import add_new_admin_user
from pac.setup import is_setup_complete
from pac.setup import set_setup_to_complete

class SetupRequestHandler(BaseHandler):
    def get(self, **kwargs):
        if is_setup_complete():
            try:
                self.redirect(self.auth_config['login_url'], abort=True)
            except (AttributeError, KeyError), e:
                self.abort(500)

        return self.render_response('edit/setup.html')

    def post(self, **kwargs):
        status = dict(status_code=1, message='', redirect=self.request.url)

        add_new_admin_user(self.auth, self.request.POST, status)

        self.auth.session.add_flash(status, key='status')

        if status['status_code'] == 1:
            set_setup_to_complete()
            # User is created, let's try redirecting to login page
            try:
                status['redirect'] = self.auth_config['login_url']
            except (AttributeError, KeyError), e:
                self.abort(500)

        self.redirect(status['redirect'])
