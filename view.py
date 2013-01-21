import webapp2
import logging
import urlparse

import models
import utils

from gaesessions import get_current_session
from google.appengine.ext import db
from google.appengine.ext import blobstore

class ViewHandler(webapp2.RequestHandler):
	def get(self):
		
		#grab session
		session = get_current_session()
		camera_keys = session.get("cameras")
		cameras = db.get(camera_keys)
		
		#get photos
		photos = []
		for camera in cameras:
			pc = models.Photo.gql('WHERE ANCESTOR IS :1',camera).fetch(None)
			photos.extend(pc)
		
		#sort by date
		photos.sort(key = lambda x: x.timestamp)
		photos.reverse()
		
		template_values = {
			"photos"	:	photos
		}
		
		utils.respond(self,'templates/view.html',template_values)
		

class ViewAllHandler(webapp2.RequestHandler):
	def get(self):
		
		#get base url
		o = urlparse.urlparse(self.request.url)
		s = urlparse.urlunparse((o.scheme, o.netloc, '', '', '', ''))
		
		photos = models.Photo.gql("ORDER BY timestamp DESC").fetch(None)
# 		photos.reverse()
		for photo in photos:
# 			photo.key().parent())
			camera = db.get(photo.key().parent())
			img_path = s+'/photo/'+str(photo.blob_key.key())
			self.response.out.write('<p><h3>{0} from camera {2}:</h3><a href="{1}"><img src="{1}" style="width:400;height:auto;"></a></p>'.format(photo.timestamp,img_path,camera.camera_id))

app = webapp2.WSGIApplication([
	('/view',ViewHandler),
	('/view/all',ViewAllHandler)
],debug=True)