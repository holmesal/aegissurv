import webapp2
import logging
import jinja2
import os
import utils
import models


class SignupHandler(webapp2.RequestHandler):
	def get(self):
		
		utils.session_bounce()
		
		jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
		template = jinja_environment.get_template('templates/signup.html')
		self.response.out.write(template.render())
	
	def post(self):
		
		email = self.request.get('email')
		pw1 = self.request.get('pw1')
		pw2 = self.request.get('pw2')
		
		


app = webapp2.WSGIApplication([
	('/signup',SignupHandler)
],debug=True)