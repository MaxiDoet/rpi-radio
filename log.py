import sys
from datetime import datetime

from colorama import Fore, Back, Style

# You can override this
TEXT_COLOR=Fore.WHITE
INFO_COLOR=Back.BLUE
WARN_COLOR=Back.YELLOW
ERROR_COLOR=Back.RED
DEBUG_COLOR=Back.MAGENTA
TIME_FORMAT="%H:%M:%S"

def _time(format):
	return datetime.now().strftime(format)

def info(text):
	print(TEXT_COLOR,_time(TIME_FORMAT),INFO_COLOR, "INFO",Style.RESET_ALL,TEXT_COLOR,text)

def warn(text):
	print(TEXT_COLOR,_time(TIME_FORMAT),WARN_COLOR, "WARN",Style.RESET_ALL,TEXT_COLOR,text)

def err(text):
	print(TEXT_COLOR,_time(TIME_FORMAT),ERROR_COLOR, "ERROR",Style.RESET_ALL,TEXT_COLOR,text)

def debug(text):
	print(TEXT_COLOR,_time(TIME_FORMAT),DEBUG_COLOR, "DEBUG",Style.RESET_ALL,TEXT_COLOR,text)
