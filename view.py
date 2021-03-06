import webapp2
import logging
import urlparse

import models
import utils

import json

from gaesessions import get_current_session
from google.appengine.ext import db
from google.appengine.ext import blobstore

class ViewHandler(webapp2.RequestHandler):
	def get(self):
		
		utils.session_bounce(self)
		
		specific = self.request.get('camera',None)
		offset = int(self.request.get('offset',0))
		if specific:
			view_all = False
		else:
			view_all = True
		
		#grab session
		session = get_current_session()
		camera_keys = session.get("cameras",[])
		cameras = db.get(camera_keys)
		
		logging.info(session)
		logging.info(cameras)
		
		#get photos
		photos = []
		for camera in cameras:
			
			logging.info(camera)
			
			if specific:
				if camera.camera_id == specific:
					try:
						pc = models.Photo.gql('WHERE ANCESTOR IS :1 ORDER BY timestamp DESC',camera).fetch(30,offset)
						photos.extend(pc)
						camera.active = True
					except Exception, e:
						logging.error(e)
			else:
				try:
					pc = models.Photo.gql('WHERE ANCESTOR IS :1 ORDER BY timestamp DESC',camera).fetch(30,offset)
					photos.extend(pc)
				except Exception, e:
					logging.error(e)
		
		#sort by date
		# photos.sort(key = lambda x: x.timestamp)
# 		photos.reverse()
		
		#readable datetime
		for photo in photos:
			photo.human_time = photo.timestamp.strftime("%A, %d %B %Y %I:%M %p")
			logging.info(photo.human_time)
		
		#break into lists of three
		counter = 0
		photos_outer = []
		temp_list = []
		
		for idx,photo in enumerate(photos):
			temp_list.append(photo)
			
			counter += 1
			
			if idx == len(photos) - 1:
				photos_outer.append(temp_list)
			else:			
				if counter == 3:
					photos_outer.append(temp_list)
					temp_list = []
					counter = 0
		
		logging.info(photos_outer)
		
		if len(photos) < 30:
			older = None
		else:
			if specific:
				older = "/view?camera="+specific+"&offset="+str(offset+30)
			else:
				older = "/view?offset="+str(offset+30)
		
		if offset == 0:
			newer = None
		else:
			if specific:
				newer = "/view?camera="+specific+"&offset="+str(offset-30)
			else:
				newer = "/view?offset="+str(offset-30)
		
		if specific:
			camera_keys = [specific]
		
		template_values = {
			"photos_outer"	:	photos_outer,
			"cameras"	:	cameras,
			"view_all"	:	view_all,
			"offset"	:	offset,
			"older"		:	older,
			"newer"		:	newer,
			"specific"	:	specific,
			"camera_keys":	[str(x) for x in camera_keys]
		}
		
		utils.respond(self,'templates/view.html',template_values)


class ViewAllHandler(webapp2.RequestHandler):
	def get(self):
		
		#get base url
		o = urlparse.urlparse(self.request.url)
		s = urlparse.urlunparse((o.scheme, o.netloc, '', '', '', ''))
		
		photos = models.Photo.gql("ORDER BY timestamp DESC").fetch(None)
# 		photos.reverse()
		for photo in photos:
# 			photo.key().parent())
			camera = db.get(photo.key().parent())
			img_path = s+'/photo/'+str(photo.blob_key.key())
			self.response.out.write('<p><h3>{0} from camera {2}:</h3><a href="{1}"><img src="{1}" style="width:400;height:auto;"></a></p>'.format(photo.timestamp,img_path,camera.camera_id))


class ViewAjaxHandler(webapp2.RequestHandler):
	def get(self):
		
		logging.info("THIS IS AN AJAX CALL")
		
		input = json.loads(self.request.params.items()[0][0])
		
		camera_keys = input.get("camera_keys")
		specific = input.get('specific',None)
		offset = int(input.get('offset',0))
		if specific:
			view_all = False
		else:
			view_all = True
		
		#grab session
# 		session = get_current_session()
# 		camera_keys = session.get("cameras",[])
		cameras = db.get(camera_keys)
		
# 		logging.info(session)
		logging.info(cameras)
		
		#get photos
		photos = []
		for camera in cameras:
			
			logging.info(camera)
			
			if specific:
				if camera.camera_id == specific:
					try:
						pc = models.Photo.gql('WHERE ANCESTOR IS :1 ORDER BY timestamp DESC',camera).fetch(30,offset)
						photos.extend(pc)
						camera.active = True
					except Exception, e:
						logging.error(e)
			else:
				try:
					pc = models.Photo.gql('WHERE ANCESTOR IS :1 ORDER BY timestamp DESC',camera).fetch(30,offset)
					photos.extend(pc)
				except Exception, e:
					logging.error(e)
		
		#sort by date
		# photos.sort(key = lambda x: x.timestamp)
# 		photos.reverse()
		
		#readable datetime
		for photo in photos:
			photo.human_time = photo.timestamp.strftime("%A, %d %B %Y %I:%M %p")
# 			logging.info(photo.human_time)
		
		#break into lists of three
		counter = 0
		photos_outer = []
		temp_list = []
		
		for idx,photo in enumerate(photos):
			photo = {
				"blob_key"	:	str(photo.blob_key.key()),
				"human_time":	photo.human_time,
				"camera"	:	photo.parent().camera_name
			}
			temp_list.append(photo)
			
			counter += 1
			
			if idx == len(photos) - 1:
				photos_outer.append(temp_list)
			else:			
				if counter == 3:
					photos_outer.append(temp_list)
					temp_list = []
					counter = 0
		
		if len(photos) < 30:
			end = True
		else:
			end = False
		
		logging.info(photos_outer)
		
		response = {
			"photos_outer" :	photos_outer,
			"end"			:	end,
			"offset"		:	offset+len(photos)
		}
		
		self.response.out.write(json.dumps(response))

class ViewCamerasHandler(webapp2.RequestHandler):
	def get(self):
		
		utils.session_bounce(self)
		
		#grab session
		session = get_current_session()
		camera_keys = session.get("cameras",[])
		cameras = db.get(camera_keys)
		
		template_values = {
			"cameras"	:	cameras if cameras != [None] else []
		}
		
		logging.info(template_values)
		
		
		utils.respond(self,'templates/managecameras.html',template_values)

class RemoveCameraHandler(webapp2.RequestHandler):
	def get(self):
		
		to_delete = self.request.get("camera",None)
		
		#get user
		session = get_current_session()
		user = db.get(session.get("user",None))
		#remove cam
		user.cameras.remove(db.Key(to_delete))
		#save
		user.put()
		#update session
		session["cameras"] = user.cameras
		session.save()
		
		
		self.redirect('/view/cameras')


app = webapp2.WSGIApplication([
	('/view',ViewHandler),
	('/view/all',ViewAllHandler),
	('/view/ajax',ViewAjaxHandler),
	('/view/cameras',ViewCamerasHandler),
	('/view/removecamera',RemoveCameraHandler)
],debug=True)