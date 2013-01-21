import webapp2
import logging
import os
import utils
import models
from google.appengine.ext import db

from gaesessions import get_current_session


class LinkHandler(webapp2.RequestHandler):
	def get(self):
		
		logging.info(get_current_session())
		
		template_values = {}
		utils.respond(self,'templates/link.html',template_values)
		
	
	def post(self):
		
		camera_id = self.request.get('camera_id')
		
		camera = models.Camera.gql("WHERE camera_id=:1",camera_id).get()
		
		if not camera:
			template_values = {
				"error"		:	"Camera ID not found. Please try again.",
				"camera_id"	:	camera_id
			}
			utils.respond(self,'templates/link.html',template_values)
		else:
			#get current user
			session = get_current_session()
			user = db.get(session['user'])
			
			#add camera
			user.cameras.append(camera.key())
			#unique
			user.cameras = list(set(user.cameras))
			user.put()
			
			#store in session
			s_cameras = session.get('cameras',[])
			s_cameras.append(camera.key())
			session['cameras'] = list(set(s_cameras))
			session.save()
			
			self.redirect('/manage')
		


app = webapp2.WSGIApplication([
	('/link',LinkHandler)
],debug=True)