class BaseViewModel(object):
    show_in_menu = False

    def __init__(self):
        className = str(self.__class__.__name__)
        self.html_view = '/edit/%s' % className.replace('ViewModel', '_view').lower() + '.html'

        self.menu_list = []


class MainViewModel(BaseViewModel):
    show_in_menu = True


class PagesViewModel(BaseViewModel):
    show_in_menu = True

    def __init__(self):
        super(PagesViewModel, self).__init__()
        self.current_page = False