from pac import view_controllers

def get_view_controller(path):
    if path == '':
        view_controller_string = 'MainViewController'
    else:
        path = path.split('/')
        view_controller_string = '%sViewController' % path[0]

    try:
        return getattr(view_controllers, view_controller_string)
    except AttributeError:
        raise NotImplementedError('No ViewController with name "%s" found.' % view_controller_string)