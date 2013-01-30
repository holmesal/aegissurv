from google.appengine.ext import db
import binascii
import jinja2
import logging
import models
import os
import utils
import webapp2
import csv
import random
import string
from google.appengine.ext import db
import json

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
class NewCameraHandler(webapp2.RequestHandler):
	def get(self):
		
		self.response.out.write('<form action="/admin/newcamera" method="post"><h3>Press the button to create a new camera and get a camera ID</h3><input type="submit" value="Generate camera"></form>')
		
	def post(self):
		#generate a new camera id
		camera_id = binascii.b2a_hex(os.urandom(10))
		
		#create and store a new camera
		camera = models.Camera(camera_id=camera_id).put()
		
		self.response.out.write('<h1>camera_id:</h1><h3>'+camera_id+'</h3>')
		
		
class ManageUsersHandler(webapp2.RequestHandler):
	def get(self):
		''' Admin is reviewing all users who have purchased cameras
		'''
		projection = ['name','email','cameras']
		# get all users
		users = models.User.all(projection=projection).order('name').run()
		user_dicts = []
		for user in users:
			# convert user to dict so we can add cams property
			user_dict = dict([(x,getattr(user,x)) for x in projection])
			user_dict['cams'] = db.get_async(user.cameras)
			user_dicts.append(user_dict)
		template_values = {
						'users' : user_dicts
						}
		template = jinja_environment.get_template('templates/manageusers.html')
		self.response.out.write(template.render(template_values))
class UsersCSVHandler(webapp2.RequestHandler):
	def get(self):
		'''Admin is requesting a csv of all users
		'''
		# set response headers
		self.response.headers['Content-Type'] = 'application/csv'
		# initialize the csv writer to write out to response
		writer = csv.writer(self.response.out)
		# iterate over all users
		for user in models.User.all(projection=('name','email','camsbought')).order('name').run():
			# write out name, email, num cameras
			writer.writerow([user.name,user.email,user.camsbought])
		
class TestHandler(webapp2.RequestHandler):
	def get(self):
		'''Spoof a bunch of users
		'''
#		assert False, 'dont be here'
		cam = models.Camera(camera_id='1').put()
		cam_list = [cam,]
		futs = []
		for i in range(1,50):
			users = []
			for c in string.ascii_letters:
				s = c*i
				users.append(models.User(
								cameras = cam_list,
								email = s,
								pw = s,
								tz = s,
								name = s,
								addr1 = s,
								city = s,
								state = 'MA',
								stripe_customer_id = s,
								camsbought = random.choice(range(1,10))
								))
			futs.append(db.put_async(users))
		# complete datastore transaction
		l = [f.get_result() for f in futs]
		self.response.out.write('Done!')
		
app = webapp2.WSGIApplication([
	('/admin/newcamera',NewCameraHandler),
	('/admin/manage_users',ManageUsersHandler),
#	('/admin/fetch_more_users',GetUsersAJAXHandler),
	('/admin/users_csv',UsersCSVHandler),
	('/admin/test',TestHandler)
],debug=True)