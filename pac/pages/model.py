from ndb import model

class dbPages(model.Model):
    name = model.StringProperty()
    view_model = model.StringProperty()
    path = model.StringProperty()
    sort_index = model.IntegerProperty(default=0)

    @property
    def page_modules(self):
        return dict([(module.identifier, module.content) for module in dbPageModules.query(ancestor=self).fetch(100)])

class dbPageModules(model.Model):
    identifier = model.StringProperty()
    content = model.TextProperty()