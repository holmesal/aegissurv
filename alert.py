import webapp2
import logging
import os
import utils
import models
from google.appengine.ext import db
from datetime import datetime,time

from gaesessions import get_current_session


class AddAlertHandler(webapp2.RequestHandler):
	def get(self):
		
		utils.session_bounce(self)
		
		#grab session
# 		session = get_current_session()
# 		camera_keys = session.get("cameras")
# 		cameras = db.get(camera_keys)
# 		
# 		logging.info(get_current_session())
		
		template_values = {
			
		}
		utils.respond(self,'templates/addalert.html',template_values)
		
	
	def post(self):
		
		#get input type
		alerttype = self.request.get('alerttype')
		
		#get current user
		session = get_current_session()
		user = session['user']
		
		if alerttype == 'justonce':
			stringstart = self.request.get('justonce-start')
			stringend = self.request.get('justonce-end')
			
			logging.info(stringstart)
			logging.info(stringend)
			start = datetime.strptime(stringstart,"%m/%d/%Y %I:%M:%S %p")
			end = datetime.strptime(stringend,"%m/%d/%Y %I:%M:%S %p")
			
			#invert if mistake
			if start > end:
				tmp = end
				end = start
				start = tmp
			
			logging.info(start)
			logging.info(end)
			
			#make alert
			alert = models.Alert(alerttype=alerttype,justoncestart=start,justonceend=end,parent=user).put()
			
		
		elif alerttype == 'recurring':
			stringstart = self.request.get('recurring-start')
			stringend = self.request.get('recurring-end')
			
			logging.info(stringstart)
			logging.info(stringend)
			
			parse_start = datetime.strptime(stringstart,"%I:%M:%S %p")
			start = parse_start.time()
			parse_end = datetime.strptime(stringend,"%I:%M:%S %p")
			end = parse_end.time()
			
			logging.info(start)
			logging.info(end)
			
			#make alert
			alert = models.Alert(alerttype=alerttype,recurringstart=start,recurringend=end,parent=user).put()

class ManageAlertHandler:
	def get(self):
		
		utils.session_bounce(self)
		
		#get current user
		session = get_current_session()
		user = session['user']
		
		#get all alerts
		alerts = models.Alert.gql('WHERE ANCESTOR IS :1',user).fetch(None)
		logging.info(alerts)


app = webapp2.WSGIApplication([
	('/alert/set',AddAlertHandler),
	('/alert/manage',ManageAlertHandler)
],debug=True)