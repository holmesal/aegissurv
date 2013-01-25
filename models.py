from google.appengine.ext import db
from google.appengine.ext import blobstore

class Photo(db.Model):
	blob_key = blobstore.BlobReferenceProperty()
	timestamp = db.DateTimeProperty()

class Camera(db.Model):
	camera_id = db.StringProperty()
	camera_name = db.StringProperty(default='Unnamed Camera')
	
class User(db.Model):
	cameras = db.ListProperty(db.Key)
	email = db.StringProperty()
	pw = db.StringProperty()

class Alert(db.Model):
	alerttype = db.StringProperty()
	justoncestart = db.DateTimeProperty()
	justonceend = db.DateTimeProperty()
	recurringstart = db.TimeProperty()
	recurringend = db.TimeProperty()
	
	
#want multiple people to be able to access cameras?
#set datetime format in stone