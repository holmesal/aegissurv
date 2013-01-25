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
		
		utils.session_bounce(self)
		
		specific = self.request.get('camera',None)
		if specific:
			view_all = False
		else:
			view_all = True
		
		#grab session
		session = get_current_session()
		camera_keys = session.get("cameras",[])
		cameras = db.get(camera_keys)
		
		logging.info(session)
		logging.info(cameras)
		
		#get photos
		photos = []
		for camera in cameras:
			
			logging.info(camera)
			
			if specific:
				if camera.camera_id == specific:
					try:
						pc = models.Photo.gql('WHERE ANCESTOR IS :1',camera).fetch(None)
						photos.extend(pc)
						camera.active = True
					except Exception, e:
						logging.error(e)
			else:
				try:
					pc = models.Photo.gql('WHERE ANCESTOR IS :1',camera).fetch(None)
					photos.extend(pc)
				except Exception, e:
					logging.error(e)
		
		#sort by date
		photos.sort(key = lambda x: x.timestamp)
		photos.reverse()
		
		#readable datetime
		for photo in photos:
			photo.human_time = photo.timestamp.strftime("%A, %d %B %Y %I:%M %p")
			logging.info(photo.human_time)
		
		#break into lists of three
		counter = 0
		photos_outer = []
		temp_list = []
		
		for idx,photo in enumerate(photos):
			temp_list.append(photo)
			
			counter += 1
			
			if idx == len(photos) - 1:
				photos_outer.append(temp_list)
			else:			
				if counter == 3:
					photos_outer.append(temp_list)
					temp_list = []
					counter = 0
		
		logging.info(photos_outer)
		
		template_values = {
			"photos_outer"	:	photos_outer,
			"cameras"	:	cameras,
			"view_all"	:	view_all
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