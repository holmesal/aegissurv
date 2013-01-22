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
	
	
#want multiple people to be able to access cameras?
#set datetime format in stone