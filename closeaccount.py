import webapp2
import logging
import os
import utils
import models
from google.appengine.ext import db

from gaesessions import get_current_session


class CloseAccountHandler(webapp2.RequestHandler):
	def get(self):
		
		utils.session_bounce(self)
		
		template_values = {}
		
		utils.respond(self,'templates/cancel.html',template_values)
	
	def post(self):
		
		logging.info("closing account...")
		
		utils.session_bounce(self)
		
		#grab session
		session = get_current_session()
		camera_keys = session.get("cameras")
		db.delete(session['user'])
		db.delete(camera_keys)
		session.terminate()
		
		logging.info(session)
		
		self.redirect('/')


app = webapp2.WSGIApplication([
	('/closeaccount',CloseAccountHandler)
],debug=True)