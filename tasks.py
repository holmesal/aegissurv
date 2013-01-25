from datetime import datetime
from google.appengine.ext import db
import logging
import webapp2

from google.appengine.api import mail

import models

class NotificationHandler(webapp2.RequestHandler):
	def post(self):
			
		logging.info('''
			
			EMAIL ALERT CHECK TASK RUNNING
			
			''')

		camera_key = db.Key(self.request.get('camera_key'))
		string_time = self.request.get('string_time')
		
		owners = models.User.gql("WHERE cameras=:1",camera_key).fetch(None)
		logging.info(owners)
		
		timestamp = datetime.strptime(string_time,"%Y%m%d-%H%M%S")
		logging.info(repr(timestamp))
		
		
		
		# for owner in owners:
# 			message = mail.EmailMessage(sender="Aegis Surveillance <connorkingman@aegissurveillance.com>", subject="Movement detected")
# 			message.to = owner.email
# 			message.body = """
# 				Motion detected
# 			"""
# 			
# 			message.send()

			
app = webapp2.WSGIApplication([('/tasks/notification', NotificationHandler)
								],debug=True)