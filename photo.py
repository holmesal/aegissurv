import webapp2
import logging
import urllib

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

class PhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, resource):
		resource = str(urllib.unquote(resource))
		blob_info = blobstore.BlobInfo.get(resource)
		self.send_blob(blob_info)

app = webapp2.WSGIApplication([
	('/photo/([^/]+)?',PhotoHandler)
],debug=True)