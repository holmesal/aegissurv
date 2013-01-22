import logging
from gaesessions import get_current_session
import jinja2
import os

def session_bounce(self):
	session = get_current_session()
	state = session.get('logged_in',False)
	
	if state == False:
		self.redirect('/login')
		
		
def respond(self,html,template_values):
	jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
	template = jinja_environment.get_template(html)
	self.response.out.write(template.render(template_values))