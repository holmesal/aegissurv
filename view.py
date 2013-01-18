import webapp2
import logging
import urlparse

import models

from google.appengine.ext import db
from google.appengine.ext import blobstore

class ViewHandler(webapp2.RequestHandler):
	def get(self):
		
		#get base url
		o = urlparse.urlparse(self.request.url)
		s = urlparse.urlunparse((o.scheme, o.netloc, '', '', '', ''))
		
		q = db.Query(models.Photo)
		photos = q.fetch(None)
		for photo in photos:
			img_path = s+'/photo/'+str(photo.blob_key.key())
			self.response.out.write('<p><img src="%s"></p>' % img_path)

app = webapp2.WSGIApplication([
	('/view',ViewHandler)
],debug=True)