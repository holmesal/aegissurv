import webapp2
import logging
import os
import utils
import models

import re

from gaesessions import get_current_session


class SignupHandler(webapp2.RequestHandler):
	def get(self):
		
		logging.info(get_current_session())
		
		template_values = {}
		utils.respond(self,'templates/signup.html',template_values)
	
	def post(self):
		
		email = self.request.get('email').lower()
		pw1 = self.request.get('pw1')
		pw2 = self.request.get('pw2')
		
		existing = models.User.gql("WHERE email=:1",email).get()
		
		if existing:
			template_values = {
				"error"		:	"That user already exists. <a href='/login'>Sign in</a>"
			}
			utils.respond(self,'templates/signup.html',template_values)
		else:

			if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
				template_values = {
				"error"		:	"Please enter a valid email address",
				"pw1"		:	pw1,
				"pw2"		:	pw2
				}
				utils.respond(self,'templates/signup.html',template_values)
			else:
				if pw1 != pw2:
					template_values = {
					"error"		:	"Passwords must match",
					"email"		:	email
					}
					utils.respond(self,'templates/signup.html',template_values)
				else:
					if len(pw1) < 6:
						template_values = {
						"error"		:	"Passwords must be at least 6 characters",
						"email"		:	email
						}
						utils.respond(self,'templates/signup.html',template_values)
					else:
						
# 						create the user
						user = models.User(email=email,pw=pw1)
						user.put()
						
						#store in session
						session = get_current_session()
						logging.info(session)
						session.clear()
						logging.info(session)
						session['logged_in'] = True
						session['user'] = user.key()
						session.save()
						
						self.redirect('/link')
		
		
		


app = webapp2.WSGIApplication([
	('/signup',SignupHandler)
],debug=True)