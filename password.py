import webapp2
import logging
import os
import utils
import models
from google.appengine.ext import db

from gaesessions import get_current_session


class PasswordHandler(webapp2.RequestHandler):
	def get(self):
		
		utils.session_bounce(self)
		
		#grab session
		session = get_current_session()
		camera_keys = session.get("cameras")
		cameras = db.get(camera_keys)
		
		logging.info(get_current_session())
		
		template_values = {
			"cameras"	:	cameras
		}
		utils.respond(self,'templates/password.html',template_values)
		
	
	def post(self):
		
		#grab inputs
		oldpw = self.request.get('oldpw')
		pw1 = self.request.get('pw1')
		pw2 = self.request.get('pw2')
		
		#grab session
		session = get_current_session()
		camera_keys = session.get("cameras",[])
		cameras = db.get(camera_keys)
		
		#check existing password
		user = db.get(session['user'])
		success = None
		if oldpw == user.pw:
			if pw1 == pw2:
				if len(pw1) > 5:
					user.pw = pw1
					user.put()
					
					success = "Your password has been successfully changed."
					error = None
					oldpw = ""
					pw1 = ""
					pw2 = ""
				else:
					error = "Passwords should be at least 5 characters."
					pw1 = ""
					pw2 = ""
			else:
				error = "New passwords do not match. Please try again."
				pw1 = ""
				pw2 = ""
		else:
			error = "Incorrect existing password. Please try again."
			oldpw = ""
		
		template_values = {
			"error"		:	error,
			"success"	:	success,
			"oldpw"		:	oldpw,
			"pw1"		:	pw1,
			"pw2"		:	pw2
		}
		
		utils.respond(self,'templates/password.html',template_values)
		


app = webapp2.WSGIApplication([
	('/password',PasswordHandler)
],debug=True)