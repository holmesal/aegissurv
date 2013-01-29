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
		
# 		grab session
		session = get_current_session()
		camera_keys = session.get("cameras")
		cameras = db.get(camera_keys)
		
		logging.info(get_current_session())
		
		template_values = {
			"cameras"		:cameras
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
		
		self.redirect('/alert/manage')

class ManageAlertHandler(webapp2.RequestHandler):
	def get(self):
		
		utils.session_bounce(self)
		
		#get current user
		session = get_current_session()
		camera_keys = session.get("cameras")
		cameras = db.get(camera_keys)
		user = session['user']
		
		#get all alerts
		alerts = models.Alert.gql('WHERE ANCESTOR IS :1',user).fetch(None)
		logging.info(alerts)
		
		#segregate
		justonce = []
		recurring = []
		for alert in alerts:
			if alert.alerttype == 'justonce':
				alert.stringstart = alert.justoncestart.strftime("%m/%d/%Y %I:%M:%S %p")
				alert.stringend = alert.justonceend.strftime("%m/%d/%Y %I:%M:%S %p")
				justonce.append(alert)
			elif alert.alerttype == 'recurring':
				alert.stringstart = alert.recurringstart.strftime("%I:%M:%S %p")
				alert.stringend = alert.recurringend.strftime("%I:%M:%S %p")
				recurring.append(alert)
		
		logging.info(justonce)
		logging.info(recurring)
		
		template_values = {
			"justonce"		:	justonce,
			"recurring"		:	recurring,
			"cameras"		:	cameras
		}
		
		utils.respond(self,'templates/managealert.html',template_values)
		
class RemoveAlertHandler(webapp2.RequestHandler):
	def get(self):
		
		utils.session_bounce(self)
		
		#get current user
		session = get_current_session()
		user = session['user']
		
		#get requested alert
		alertdel = self.request.get('alert')
		
		#find requested alert
		alert = db.get(alertdel)
		logging.info(alert)
		if alert.key().parent() == user:
			alert.delete()
		
		self.redirect('/alert/manage')


app = webapp2.WSGIApplication([
	('/alert/set',AddAlertHandler),
	('/alert/manage',ManageAlertHandler),
	('/alert/remove',RemoveAlertHandler)
],debug=True)