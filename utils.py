import logging
from gaesessions import get_current_session
import jinja2
import os

def session_bounce(self):
	session = get_current_session()
	if session.has_key('logged_in'):
		if session['logged_in']:
			pass
	else:
		self.redirect('/login')
		
def respond(self,html,template_values):
	jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
	template = jinja_environment.get_template(html)
	self.response.out.write(template.render(template_values))