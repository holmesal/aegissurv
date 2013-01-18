import webapp2
import logging

import models

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

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
		logging.info(token)
		
		
		upload_files = self.get_uploads('file')
		blob_info = upload_files[0]
# 		self.redirect('/serve/%s' % blob_info.key())
		time = int(self.request.get("time"))
		
		photo = models.Photo(blob_key=blob_info,time=time)
		photo.put()
		
		self.response.out.write(500)

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