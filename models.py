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
	#properties from order process
	tz = db.StringProperty()
	name = db.StringProperty()
	addr1 = db.StringProperty()
	addr2 = db.StringProperty()
	city = db.StringProperty()
	state = db.StringProperty()
	stripe_customer_id = db.StringProperty()
	camsbought = db.IntegerProperty(default=0)

class Alert(db.Model):
	alerttype = db.StringProperty()
	justoncestart = db.DateTimeProperty()
	justonceend = db.DateTimeProperty()
	recurringstart = db.TimeProperty()
	recurringend = db.TimeProperty()

class Purchase(db.Model):
	status = db.StringProperty(required=True,choices=set(["not_charged","success","fail"]))
	numcams = db.IntegerProperty(required=True)
	charge_token = db.StringProperty(required=True)
	amount = db.IntegerProperty(required=True) #in cents, always
	
	
#want multiple people to be able to access cameras?
#set datetime format in stone