"""
    All ViewController classes has an attached ViewModel with the same name. The ViewController will try find it's
    match and invoke it.

    Ie:
    MainViewController has a attached ViewModel called MainViewModel (located in /pac/view_models/__init__.py)
"""
import inspect
from pac import view_models
from pac import pages

class BaseViewController(object):
    """Base class for all admin panel handlers."""

    def __init__(self, app=False, request=False, auth=False):
        self.app = app
        self.request = request
        self.auth = auth

        className = str(self.__class__.__name__)
        try:
            cls = getattr(view_models, className.replace('ViewController', 'ViewModel'))
            self.view_model = cls()
        except AttributeError:
            self.view_model = False

        if self.view_model:
            self.view_model.menu_list = [name.replace('ViewModel', '') for name, cls in inspect.getmembers(view_models) if inspect.isclass(view_models.BaseViewModel) and hasattr(cls, 'show_in_menu') and getattr(cls, 'show_in_menu')]


class MainViewController(BaseViewController):
    pass

class PagesViewController(BaseViewController):
    def __init__(self):
        super(PagesViewController, self).__init__()

        if self.request and self.request.args.get('item_id'):
            self.view_model.current_page = pages.get_by_id(self.request.args.get('item_id'))