import webapp2
import logging
import os
import utils
import models

from gaesessions import get_current_session


class LoginHandler(webapp2.RequestHandler):
	def get(self):
		
		session = get_current_session()
		if session.get('logged_in',False) == True:
			self.redirect('/view')
		
		template_values = {}
		utils.respond(self,'templates/login.html',template_values)
		
		
	def post(self):
		
		email = self.request.get('email').lower()
		pw = self.request.get('pw')
		
		existing = models.User.gql('WHERE email=:1 AND pw=:2',email,pw).get()
		logging.info(existing)
		
		if existing:
			session = get_current_session()
			session.clear()
			session['logged_in'] = True
			session['cameras'] = existing.cameras
			session['user'] = existing.key()
			session.save()
			
			#cameras linked?
			if len(session.get('cameras',[])) > 0:
				self.redirect('/view')
			else:
				self.redirect('/link')
		
		else:
			template_values = {
				"error"		:	"Try again"
			}
			utils.respond(self,'templates/login.html',template_values)
		


app = webapp2.WSGIApplication([
	('/login',LoginHandler)
],debug=True)