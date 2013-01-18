'''
Modules required:

poster
urllib2
'''

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

#PARAMETERS
camera_id = 'somecameraid'
token = 'somehardcodedtoken'
local = True		#set to true to use localhost FOR TESTING, false to use appspot

def get_upload_url():
	#get the upload url from GAE
	urlrequest = urllib2.urlopen(base_url+"/upload/geturl")
	upload_url = urlrequest.read()
	return upload_url

def post_image(filename,time):
	# Register the streaming http handlers with urllib2
	register_openers()
	
	datagen, headers = multipart_encode({"file": open("testimg.png"),"time":time,"camera_id":camera_id,"token":token})
	
	request = urllib2.Request(upload_url, datagen, headers)
	
	response =  urllib2.urlopen(request).read()
	print response
	if response == '200':
		#delete files here
		print('RESPONSE OKAY FILE DELETED')
	else:
		print('RESPONSE ERROR FILE NOT DELETED')


#build base url
if local == True:
	base_url = 'http://localhost:8096'
else:
	base_url = 'http://aegissurv.appspot.com'
	
#get the upload url
upload_url = get_upload_url()

#post the file
filename = 'testimg.png'
time = 92749338379
post_image(filename,time)

