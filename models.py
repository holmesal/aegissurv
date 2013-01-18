from google.appengine.ext import db
from google.appengine.ext import blobstore

class Photo(db.Model):
	blob_key = blobstore.BlobReferenceProperty()
	time = db.IntegerProperty()