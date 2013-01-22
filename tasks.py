from datetime import datetime
from google.appengine.api import urlfetch
from google.appengine.ext import db
import base64
import json
import logging
import urllib
import webapp2

class EmailTaskHandler(webapp2.RequestHandler):
	def post(self):
		# try:
# 			
# 			logging.info('''
# 				
# 				EMAIL ALERT CHECK TASK RUNNING
# 				
# 				''')
# 			
# 			payload = json.loads(self.request.body)
# 			logging.info(payload['artist_name'])
# 			
# 			
# 			
# 		except:
# 			logging.debug('Ah man this failed')
		pass

			
app = webapp2.WSGIApplication([('/tasks/emailTask', EmailTaskHandler)
								],debug=True)