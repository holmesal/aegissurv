import webapp2
import logging
import os
import utils
import models

from gaesessions import get_current_session


class LogoutHandler(webapp2.RequestHandler):
	def get(self):
		
		session = get_current_session()
		
		session['logged_in'] = False
		session.save()
		
		self.redirect('/login')
	
	def post(self):
		
		email = self.request.get('email').lower()
		pw1 = self.request.get('pw1')
		pw2 = self.request.get('pw2')
		
		existing = models.User.gql("WHERE email=:1",email).get()
		
		if existing:
			template_values = {
				"error"		:	"That user already exists"
			}
			utils.respond(self,'templates/signup.html',template_values)
		else:
			#create the user
			user = models.User(email=email,pw=pw1)
			user.put()
			
			#store in session
			session = get_current_session()
			session['logged_in'] = True
			session['user'] = user.key()
			session.save()
			
			self.redirect('/link')
		


app = webapp2.WSGIApplication([
	('/logout',LogoutHandler)
],debug=True)