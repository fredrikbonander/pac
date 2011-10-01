from webapp2_extras.routes import RedirectRoute
from web.handlers import LoginHandler
from web.handlers import LogoutHandler
from web.handlers import SecureRequestHandler
from web.handlers import CreateUserHandler
from pac.handlers import RequestHandler
from pac.handlers import LoginHandler as PacLoginHandler
from pac.handlers import LogoutHandler as PacLogoutHandler
from pac.setup.handlers import SetupRequestHandler

routes = [
    RedirectRoute('/edit/setup/', SetupRequestHandler, name='pac-setup', strict_slash=True),
    RedirectRoute('/edit/login/', PacLoginHandler, name='pac-login', strict_slash=True),
    RedirectRoute('/edit/logout/', PacLogoutHandler, name='pac-logout', strict_slash=True),
    RedirectRoute('/edit/<:.*/?>', RequestHandler, name='pac', strict_slash=True),
    RedirectRoute('/login/', LoginHandler, name='login', strict_slash=True),
    RedirectRoute('/logout/', LogoutHandler, name='logout', strict_slash=True),
    RedirectRoute('/secure/', SecureRequestHandler, name='secure', strict_slash=True),
    RedirectRoute('/<:.*/?>', CreateUserHandler, name='create-user', strict_slash=True)
]

def add_routes(app):
    for r in routes:
        app.router.add(r)
