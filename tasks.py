from datetime import datetime, timedelta
from google.appengine.ext import db
import logging
import webapp2

from google.appengine.api import mail

import models

import stripe

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
		
		for owner in owners:
			
			#default is not to notify
			notify = False
			
			#get alerts
			alerts = models.Alert.gql('WHERE ANCESTOR IS :1',owner.key()).fetch(None)
			logging.info(alerts)
			
			for alert in alerts:
				if alert.alerttype == 'justonce':
					start = alert.justoncestart
					end = alert.justonceend
					
					logging.info(timestamp > start)
					logging.info(timestamp < end)
					
					if timestamp > start and timestamp < end:
						logging.info("JUSTONCE IN RANGE")
						notify = True
					
				
				elif alert.alerttype == 'recurring':
					start = alert.recurringstart
					end = alert.recurringend
					
					now = timestamp.time()
					
					logging.info(start)
					logging.info(now)
					logging.info(end)
					
					if end > start:
						#both times are on the same day
						if now > start and now < end:
							notify = True
							logging.info("TIMES ARE ON SAME DAY AND IN RANGE")
					else:
						#the times are, for example, overnight
						if now > start or now < end:
							notify = True
							logging.info("TIMES SPAN DAYS AND IN RANGE")
			
			
			if notify == True:
				
				#get camera name
				camera = db.get(camera_key)
				camera_name = camera.camera_name
				
				#get blob serving url
				blob_key = self.request.get('blob_key')
				logging.info(blob_key)
				#send email
				message = mail.EmailMessage(sender="Aegis Surveillance <connorkingman@aegissurveillance.com>", subject="Movement detected")
				message.to = owner.email
				message.body = 'Motion detected on camera "' + camera_name + '".'
				message.html = '<h3>Motion detected on camera "' + camera_name + '".</h3>'
				message.html += '<img src="http://aegissurv.appspot.com/photo/'+blob_key+'">' 
				
				message.send()

class DeleteOldHandler(webapp2.RequestHandler):
	def get(self):
		
		#current time
		now = datetime.now()
		
		#30 days ago
		passage = timedelta(30)
		thepast = now-passage
		logging.info(thepast)
		
		oldies = models.Photo.gql('WHERE timestamp < :1',thepast)
		oldiescount = oldies.count()
		logging.info("OLDIES FOUND:")
		logging.info(oldiescount)
		db.delete(oldies)
		
		alerts = models.Alert.gql("WHERE alerttype=:1 AND justonceend < :2",'justonce',now)
		alertscount = alerts.count()
		logging.info("EXPIRED ONE-TIME ALERTS FOUND:")
		logging.info(alertscount)
		db.delete(alerts)
		
		logging.info('Finished running old entity deletion task. '+str(oldiescount)+' old photos were deleted and '+str(alertscount)+' expired one-time alerts were deleted. Have a nice day.')

class PaymentPlanHandler(webapp2.RequestHandler):
	def post(self):
		
		logging.info('''
			
			PAYMENT PLAN TASK RUNNING
			
			''')

		user_key = db.Key(self.request.get('user_key'))
		
		#stripe api key
		stripe.api_key = "sk_test_rTlew3qolgnYdtV2uZfj7oZr"
		
		#get user from db
		user = db.get(user_key)
		
		#get customer from stripe
		customer = stripe.Customer.retrieve(user.stripe_customer_id)
		
		#how many cameras have they bought
		camsbought = user.camsbought
		
		#build appropriate plan
		if camsbought > 10:
			camsbought = 10
		
		plan = "plan"+str(camsbought)
		logging.info(plan)
		
		subscrip = customer.update_subscription(plan=plan)
		logging.info(subscrip)

class NewOrderHandler(webapp2.RequestHandler):
	def post(self):
		
		logging.info('''
			
			NEW ORDER TASK RUNNING
			
			''')

		purchase_key = db.Key(self.request.get('purchase_key'))
		
		purchase = db.get(purchase_key)
		
		user = db.get(purchase_key.parent())
		
		#send email
		message = mail.EmailMessage(sender="Aegis Surveillance <connorkingman@aegissurveillance.com>", subject="New Purchase")
		message.to = "Aegis Surveillance <connorkingman@aegissurveillance.com>"
		message.html = '<h1>Buyer information</h1>'
		message.html += '<p>Name: ' + user.name + '</p>'
		message.html += '<p>Email: ' + user.email + '</p>'
		message.html += '<p>Address 1: ' + user.addr1 + '</p>'
		message.html += '<p>Address 2: ' + user.addr2 + '</p>'
		message.html += '<p>City: ' + user.city + '</p>'
		message.html += '<p>State: ' + user.state + '</p>'
		message.html += '<p>Time Zone: ' + user.tz + '</p>'
		message.html += '<h1>Order Information</h1>'
		message.html += '<p>Number of cameras: ' + str(purchase.numcams) + '</p>'
		message.html += '<p>Order total: ' + str(purchase.amount) + '</p>'
		
		logging.info(message.html)
		
		logging.info(purchase)
		logging.info(user)
		
		message.send()

			
app = webapp2.WSGIApplication([('/tasks/notification', NotificationHandler),
								('/tasks/deleteold', DeleteOldHandler),
								('/tasks/paymentplan',PaymentPlanHandler),
								('/tasks/neworder',NewOrderHandler)
								],debug=True)