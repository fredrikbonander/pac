from ndb import model

class dbSettings(model.Model):
	"""
		Key-value model for storing settings

		Uses key_name as key
	"""
	value = model.StringProperty(required=True)