import webapp2
import logging
import os
import utils
import models
from google.appengine.ext import db
import re
import json
import stripe
from google.appengine.api import taskqueue

from gaesessions import get_current_session


class PurchaseHandler(webapp2.RequestHandler):
	def get(self):
		
		session = get_current_session()
		logging.info(session)
		
		if session.get("logged_in",False) == True:
			user = db.get(session.get('user'))
			
			template_values = {
				"loggedin"	:	True,
				"addr1"		:	getattr(user,'addr1',''),
				"addr2"		:	getattr(user,'addr2',''),
				"city"		:	getattr(user,'city',''),
				"state"		:	getattr(user,'state',''),
				"tz"		:	getattr(user,'tz',''),
				"name"		:	getattr(user,'name','')
			}
			
			
		else:
			template_values = {
				"loggedin"	:	False
			}
		
		
	
		utils.respond(self,'templates/purchase.html',template_values)
	
	def post(self):
		
		#grab inputs
		email = self.request.get('email')
		pw1 = self.request.get('pw1')
		pw2 = self.request.get('pw2')
		tz = self.request.get('tz')
		name = self.request.get('name')
		addr1 = self.request.get('addr1')
		addr2 = self.request.get('addr2')
		city = self.request.get('city')
		state = self.request.get('state')
		stripe_token = self.request.get('stripe_token')
		amount = self.request.get('amount')
		numcams = int(self.request.get('numcams'))
		
		logging.debug(email)
		logging.debug(pw1)
		logging.debug(pw2)
		logging.debug(tz)
		logging.debug(name)
		logging.debug(addr1)
		logging.debug(addr2)
		logging.debug(city)
		logging.debug(state)
		logging.debug(stripe_token)
		logging.debug(amount)
		logging.debug(numcams)
		
		session = get_current_session()
		logging.info(session)
		
		#set stripe api key
		stripe.api_key = "sk_test_rTlew3qolgnYdtV2uZfj7oZr"
		
		try:
		
			#user is logged in - create charge and associate with them
			if session.get("logged_in",False) == True:
				user = db.get(session.get('user'))
				
				#update the current card
				customer = stripe.Customer.retrieve(user.stripe_customer_id)
				customer.card = stripe_token
				customer.save()
			
			#user is not logged in - create a new user
			else:
				user = models.User(
					email=email,
					pw=pw1,
					tz=tz,
					name=name,
					addr1=addr1,
					addr2=addr2,
					city=city,
					state=state
				)
				
				logging.info(user)
				
				#create a new customer via stripe
				customer = stripe.Customer.create(
				  description=user.email,
				  card=stripe_token # obtained with Stripe.js
				)
				
				logging.info(customer)
				
				#add stripe customer id to user
				user.stripe_customer_id = customer["id"]
				
				#store user
				user.put()
				
				#log in
				session['logged_in'] = True
				session['user'] = user.key()
				session.save()
		
			#charge the one-time total
			charge = stripe.Charge.create(
				amount=amount,
				currency="usd",
				customer=user.stripe_customer_id,
				description="Charge for camera purchase to "+user.email
			)
		
			logging.info(charge)
		
			#increment camsbought
			user.camsbought += numcams
			user.put()
			
			#launch the task to check on the amounts
			try:
				taskqueue.add(url='/tasks/paymentplan', params={'user_key': user.key()})
			except Exception,e:
				logging.error(e)
				logging.error('Task initialization failed')
			
			
			#create a charge object and associate with the user
			purchase = models.Purchase(
				status="success",
				numcams=int(numcams),
				charge_token=stripe_token,
				amount=int(amount),
				parent=user).put()
			
			#launch the task to notify of new order
			try:
				taskqueue.add(url='/tasks/neworder', params={'purchase_key': purchase})
			except Exception,e:
				logging.error(e)
				logging.error('New order task initialization failed')
			
			#username for stripe is connorkingman@aegissurveillance.com
			#password for stripe is aegispayments
				
			logging.info(purchase)
			
			template_values = {
				"thanks"	:	True,
				"email"		:	user.email
			}
			
			utils.respond(self,'templates/purchase.html',template_values)
		
		except stripe.CardError,e:
			carderror = e
			
			loggedin = session.get('logged_in',False)
			
			template_values = {
				"email" : email,
				"pw1" : pw1,
				"pw2" : pw2,
				"tz" : tz,
				"name" : name,
				"addr1" : addr1,
				"addr2" : addr2,
				"city" : city,
				"state" : state,
				"numcams" : numcams,
				"loggedin" : loggedin,
				"carderror" : carderror
			}
			
			utils.respond(self,'templates/purchase.html',template_values)
			
		
		
		
		
class CheckEmailHandler(webapp2.RequestHandler):
	def get(self):
		
		session = get_current_session()
		logging.info(session)
		if session.get("logged_in",False) == True:
			user = db.get(session.get('user'))
			logged_in_email = user.email
		else:
			logged_in_email = ''
			
		
		email = self.request.get('email').lower()
		
		existing = models.User.gql("WHERE email=:1",email).get()
		
		error = False
		
		if existing and email != logged_in_email:
			error = "existing"
		else:
			if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
				error = "invalid"
		
		response = {
			"error"	:	error
		}
		
		self.response.out.write(json.dumps(response))


app = webapp2.WSGIApplication([
	('/purchase',PurchaseHandler),
	('/purchase/checkemail',CheckEmailHandler)
],debug=True)