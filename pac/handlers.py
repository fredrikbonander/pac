# -*- coding: utf-8 -*-

"""
	A real simple app for using webapp2 with auth and session.

	It just covers the basics. Creating a user, login, logout and a decorator for protecting certain handlers.

	PRE-REQUIREMENTS:

	Set at secret_key in webapp2 config:
	webapp2_config = {}
	webapp2_config['webapp2_extras.sessions'] = {
		'secret_key': 'Im_an_alien',
	}

	You need to either set upp the following routes:

	app = webapp2.WSGIApplication([
		webapp2.Route(r'/login/', handler=LoginHandler, name='login'),
		webapp2.Route(r'/logout/', handler=LogoutHandler, name='logout'),
		webapp2.Route(r'/login/', handler=SecureRequestHandler, name='secure'),
		webapp2.Route(r'/secure/', handler=CreateUserHandler, name='create-user'),

	])

    OR:

    Change the urls in BaseHandler.auth_config to match LoginHandler/LogoutHandler
    And also change the url in the post method of the LoginHandler to redirect to to a page requiring a user session
"""
from pac import dispatcher
from pac.auth_util import user_required

import webapp2
from webapp2_extras import auth, jinja2
from webapp2_extras import sessions
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

class BaseHandler(webapp2.RequestHandler):
    """
       BaseHandler for all requests

       Holds the auth and session properties so they are reachable for all requests
   """

    def dispatch(self):
        """
          Save the sessions for preservation across requests
        """
        try:
            response = super(BaseHandler, self).dispatch()
            self.response.write(response)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()

    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    @webapp2.cached_property
    def auth_config(self):
        """
          Dict to hold urls for login/logout
        """
        return {
            'login_url': self.uri_for('pac-login'),
            'logout_url': self.uri_for('pac-logout')
        }

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        status = self.auth.session.get_flashes(key='status')
        context_status = ''
        if len(status) > 0:
            context_status = status[0][0]

        context.update({
            'status': context_status,
            'current_url': self.request.url,
        })
        # Renders a template and writes the result to the response.
        return self.jinja2.render_template(_template, **context)


class LoginHandler(BaseHandler):
    def get(self):
        """
          Returns a simple HTML form for login
        """
        return self.render_response('edit/login.html', model=False)

    def post(self):
        """
          username: Get the username from POST dict
          password: Get the password from POST dict
      """
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        # Try to login user with password
        # Raises InvalidAuthIdError if user is not found
        # Raises InvalidPasswordError if provided password doesn't match with specified user
        try:
            self.auth.get_user_by_password(username, password)
            self.redirect('/edit/')
        except (InvalidAuthIdError, InvalidPasswordError), e:
            # Returns error message to self.response.write in the BaseHandler.dispatcher
            # Currently no message is attached to the exceptions
            status = dict(status_code=-20, message='Login error, username/password miss match')
            self.auth.session.add_flash(status, key='status')
            self.redirect(self.auth_config['login_url'])


class LogoutHandler(BaseHandler):
    """
       Destroy user session and redirect to login
   """

    def get(self):
        self.auth.unset_session()
        # User is logged out, let's try redirecting to login page
        try:
            self.redirect(self.auth_config['login_url'])
        except (AttributeError, KeyError), e:
            return "User is logged out"

class RequestHandler(BaseHandler):
    """
       Handles all requests that doesn't match any other route under path /edit/
    """
    @user_required
    def get(self, *args, **kwargs):
        view_controller_cls = dispatcher.get_view_controller(args[0])
        view_controller = view_controller_cls()

        return self.render_response(view_controller.view_model.html_view, model=view_controller.view_model)

    def post(self, *args, **kwargs):
        view_controller_cls = dispatcher.get_view_controller(args[0])
        view_controller = view_controller_cls()

        view_controller.dispatch_post(self.request.POST)

        return self.render_response(view_controller.view_model.html_view, model=view_controller.view_model)