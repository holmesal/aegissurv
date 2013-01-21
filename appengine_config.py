from gaesessions import SessionMiddleware 
from google.appengine.ext.appstats import recording
def webapp_add_wsgi_middleware(app): 
	app = SessionMiddleware(app, cookie_key="fc5a2219d2937ecca4cc737f73fd2731f5f96b4243903b957e56466ddc5f6ba3bb7e12035faca1cafcbe9fca903417a8b55a587b30fe6a3341f298182df717b5")
	app = recording.appstats_wsgi_middleware(app)
	return app
