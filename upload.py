import webapp2
import logging

import models
from datetime import datetime

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import taskqueue

class GetUrlHandler(webapp2.RequestHandler):
	def get(self):
		
		#generate the upload URL for the image blob
		upload_url = blobstore.create_upload_url('/upload/post')
		
		#write out
		self.response.out.write(upload_url)
		
class PostHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		#check the token on the request
		token = self.request.get('token')
		if token == '3g6cz8IoZ2OOhFhkZQVCJgsEtgFZVxMe':
			
			camera_id = self.request.get('camera_id')
			logging.info(camera_id)
			
			#check if camera exists
			camera = models.Camera.gql("WHERE camera_id=:1",camera_id).get()
			if not camera:
				camera = models.Camera(camera_id=camera_id).put()
		
			#grab blobinfo
			upload_files = self.get_uploads('file')
			blob_info = upload_files[0]
			
			#grab time
			string_time = self.request.get("time")
			logging.info(string_time)
			#parse time
			raw_time = datetime.strptime(string_time,"%Y%m%d-%H%M%S")
			logging.info(repr(raw_time))
			
			#store photo
			photo = models.Photo(blob_key=blob_info,timestamp=raw_time,parent=camera)
			photo.put()
			
			#fire off notification task handler
			try:
				taskqueue.add(url='/tasks/notification', params={'camera_key': camera.key(),'string_time':string_time,'blob_key':blob_info.key()})
			except Exception,e:
				logging.error(e)
				logging.error('Task initialization failed')
			
			self.response.out.write(200)
		
		else:
			self.response.out.write(403)

class TestHandler(webapp2.RequestHandler):
	def get(self):
		upload_url = blobstore.create_upload_url('/upload/post')
		self.response.out.write('<html><body>')
		self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
		self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit" name="submit" value="Submit"> </form></body></html>""")


app = webapp2.WSGIApplication([
	('/upload/geturl',GetUrlHandler),
	('/upload/post',PostHandler),
	('/upload/test',TestHandler)
],debug=True)