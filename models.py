from google.appengine.ext import db
from google.appengine.ext import blobstore

class Photo(db.Model):
	blob_key = blobstore.BlobReferenceProperty()
	timestamp = db.DateTimeProperty()

class Camera(db.Model):
	camera_id = db.StringProperty()
	
	
#want multiple people to be able to access cameras?
#set datetime format in stone