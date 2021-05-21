from datetime import time

def get_time():
	now = datetime.now()
	return now.strftime("%H:%M")

def get_date():
	now = datetime.now()
	return now.strftime("%m/%d/%y")
