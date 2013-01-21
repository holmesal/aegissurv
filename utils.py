import logging
from gaesessions import get_current_session

def session_bounce():
	session = get_current_session()
	logging.info(session)