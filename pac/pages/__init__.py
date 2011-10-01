from .model import dbPages
from .model import dbPageModules
from pac.utils import slugify

def get_parent_page(parent):
    if parent == '0':
        return None
    else:
        return get_by_id(parent)

def get_page_path(page_name):
    path = '/%s' % slugify(page_name)
    return path

def get_or_insert_page(page_id, parent_string, view_model):
    if page_id:
        page = get_by_id(page_id)
    else:
        page = dbPages(parent=get_parent_page(parent_string))
        page.view_model = view_model

    return page

def save_page(form):
    page_id = form.get('page_id') or None
    page = get_or_insert_page(page_id, form.get('parent'), form.get('template'))
    page.name = form.get('page_name')
    page.path = get_page_path(form.get('page_name'))

    try:
        page.sort_index = int(form.get('sort_index'))
    except TypeError:
        page.sort_index = 0

    return page.put()

def insert_or_update_page(form, status):
    page_key = save_page(form)

    #if form.get('startpage') == 'on':
    #    settingService.storeSettingFor('StartPageKey', str(pageKey))

    for arg in form:
        contentList = arg.split('|')
        if len(contentList) > 1 and contentList[0] == 'content_module':
            insert_or_update_page_modules(contentList[1], form.get(arg), page_key)

    status['redirect'] = '/edit/pages/?id=%s' % str(page_key.id())

    return page_key


def insert_or_update_page_modules(identifier, content, page_key):
    module = dbPageModules.query(ancestor=page_key).filter(dbPageModules.identifier == identifier).get()
    
    if not module:
        module = dbPageModules(parent=page_key)
        module.identifier = identifier

    module.content = content
    return module.put()


def get_by_id(page_id):
    if page_id:
        return dbPages.get_by_id(int(page_id))
    else:
        return None