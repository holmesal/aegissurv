'''
Modules required:

poster
urllib2
os
'''

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
import os
from datetime import datetime





#PARAMETERS
camera_id = 'alonso3'
file_end = 'jpg'	#file ending. Do not include the .
dir = './'			#relative path from python script to image file
					#"./" = same folder
					#"../"= one level up
					#"../images/"=one level up, then into "images" folder - make sure to include the final slash
					#etc
					
#TESTING ON LOCAL
local = False		#set to true to use localhost FOR TESTING, false to use remote server






###DO NOT CHANGE###
token = '3g6cz8IoZ2OOhFhkZQVCJgsEtgFZVxMe'		#Don't change this - it's hardcoded on both the python and server sides
###DO NOT CHANGE###





def parse_time(filename):
	string_time = filename[:-len(file_end)-1]
	return string_time


def findfiles():
	#uploaded count
	upload_count = 0
	#find files
	for f in os.listdir(dir):
		if f[-len(file_end):] == file_end:
			print('uploading file:'+dir+f)
			
			#upload file
			upload_url = get_upload_url()
			t = parse_time(f)
			post_image(upload_url,dir+f,t)
			
			#increment
			upload_count += 1
	
	#no files found
	if upload_count == 0:
		print('No files found that end in .'+file_end)


def get_upload_url():
	#get the upload url from GAE
	#try a maximum of 5 times
	url_attempts = 0
	while url_attempts < 5:
		try:
			urlrequest = urllib2.urlopen(base_url+"/upload/geturl")
			upload_url = urlrequest.read()
			return upload_url
		except Exception,e:
			print("Error getting upload URL")
			print(e)
			print("Retrying...")
			url_attempts += 1

def post_image(upload_url,filename,time):
	# Register the streaming http handlers with urllib2
	#try a maximum of 5 times
	upload_attempts = 0
	while upload_attempts < 5:
		try:
			register_openers()
			
			datagen, headers = multipart_encode({"file": open(filename),"time":time,"camera_id":camera_id,"token":token})
			
			request = urllib2.Request(upload_url, datagen, headers)
			
			response =  urllib2.urlopen(request).read()
			print response
			if response == '200':
				#delete files here
				os.remove(filename)
				print('RESPONSE OKAY FILE DELETED')
				return True
			else:
				print('SERVER ERROR FILE NOT DELETED')
				return False
				
		except Exception,e:
			print("Error posting file")
			print(e)
			print("Retrying...")
			upload_attempts += 1
			
	if upload_attempts == 5:
		os.remove(filename)
		print('Image was deleted after 5 failed attempts to post')
		return False

#build base url
if local == True:
	base_url = 'http://localhost:8096'
else:
	base_url = 'http://aegissurv.appspot.com'

#find files and post
findfiles()


