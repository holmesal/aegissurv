import webapp2
import logging
import os
import utils
import models

from gaesessions import get_current_session


class LandingHandler(webapp2.RequestHandler):
	def get(self):
		
		template_values = {}
		utils.respond(self,'templates/landing.html',template_values)

app = webapp2.WSGIApplication([
	('/',LandingHandler)
],debug=True)