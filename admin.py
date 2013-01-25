import webapp2
import logging
import os
import utils
import models
import binascii


class NewCameraHandler(webapp2.RequestHandler):
	def get(self):
		
		self.response.out.write('<form action="/admin/newcamera" method="post"><h3>Press the button to create a new camera and get a camera ID</h3><input type="submit" value="Generate camera"></form>')
		
	def post(self):
		#generate a new camera id
		camera_id = binascii.b2a_hex(os.urandom(10))
		
		#create and store a new camera
		camera = models.Camera(camera_id=camera_id).put()
		
		self.response.out.write('<h1>camera_id:</h1><h3>'+camera_id+'</h3>')
		
		


app = webapp2.WSGIApplication([
	('/admin/newcamera',NewCameraHandler)
],debug=True)