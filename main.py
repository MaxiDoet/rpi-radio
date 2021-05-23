import RPi.GPIO as GPIO
import json
from log import *
import time
import math
import subprocess
import utils

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

VERSION="1.0"
info("Version: %s" % VERSION)

try:
	config_fp = open("config.json", "r")
	config = json.load(config_fp)
except:
	err("No config file found!")
	exit();

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Up Button
GPIO.setup(config["pins"]["up"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# Down Button
GPIO.setup(config["pins"]["down"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# Confirm Button
GPIO.setup(config["pins"]["confirm"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Init oled
disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
disp.begin()
disp.clear()
disp.display()

width = disp.width
height = disp.height

image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
header_end = 9

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

# Radio variables
radio_frequency = 100
radio_band_start = config["fmStart"]
radio_band_end = config["fmEnd"]

# Variables
in_menu = False
alarm_triggered = False
alarm_frame = 0
alarm_frame_max = 28
menu_index = 0
menu_index_max = 0
menu_title = ""
menu_entry_height = 7
mode = 0
sleep = False
sleep_timer = config["sleep"]
sleep_last = 0

confirm_last = GPIO.LOW
confirm_pressed = 0

"""
Modes:
	0 Home
	1 Radio
	2 Media player
"""

def sleep_reset(channel):
	global sleep_timer
	sleep_timer = config["sleep"]
	#sleep = False

GPIO.add_event_detect(config["pins"]["up"],GPIO.RISING,callback=sleep_reset)
GPIO.add_event_detect(config["pins"]["down"],GPIO.RISING,callback=sleep_reset)
GPIO.add_event_detect(config["pins"]["confirm"],GPIO.RISING,callback=sleep_reset)

def draw_header():
	# Clock
	draw.text(((width - 30), top), utils.get_time(), font=font, fill=255)

	# Seperator
	draw.line((0, 8, width, 8), fill=255)

def draw_menu(title, entries, confirm_callback):
	global menu_index

	entries_count = len(entries)
	pages = int(math.ceil(entries_count / 3))

	menu_index_max = entries_count

	current_page = int(menu_index / 3)

	scrollbar_height = height / pages
	scrollbar_y = header_end + current_page * scrollbar_height

	# Scrollbar
	draw.rectangle((width-5, scrollbar_y, width, scrollbar_y + scrollbar_height), fill=255)

	#print("pages: %d current_page: %d scrollbar_height: %d scrollbar_y: %d" % (pages, current_page, scrollbar_height, scrollbar_y))

	# Entries
	for i in range(3):
		try:
			draw.text((10, header_end + i*menu_entry_height), entries[current_page*3:current_page*3+3][i], font=font, fill=255)
		except:
			pass

	# Selected indicator
	draw.rectangle((2, header_end + (menu_index - (current_page * 3)) * menu_entry_height + 3, 4, header_end + (menu_index - (current_page * 3)) * menu_entry_height + 3 + 5), fill=255)

	if GPIO.input(config["pins"]["up"]) == GPIO.HIGH:
		sleep_timer = config["sleep"]

		if menu_index >= 0 and menu_index < menu_index_max+1:
			menu_index += 1
		else:
			menu_index = 0

	if GPIO.input(config["pins"]["down"]) == GPIO.HIGH:
		sleep_timer = config["sleep"]

		if menu_index > 0 and menu_index < menu_index_max+1:
			menu_index -= 1
		else:
			menu_index = menu_index_max

	if GPIO.input(config["pins"]["confirm"]) == GPIO.HIGH and confirm_last != GPIO.HIGH:
		sleep_timer = config["sleep"]

		if (confirm_callback != None):
			confirm_callback(menu_index)

def draw_radio(frequency, stereo):
	# Menu title
	draw.text(((width - 8*len("Radio")) / 2, top), "Radio", font=font, fill=255)

	# Frequency
	draw.text(((width - 8*len("%shz" % frequency)) / 2, height/2-5), "%shz" % frequency, font=font, fill=255)

	# Stereo indicator
	if stereo:
		draw.text((1, top), "S", font=font, fill=255)

	# Band
	band = Image.open('images/band.png').resize((128, 8), Image.ANTIALIAS).convert('1')
	image.paste(band, (0, 32-8))

	# Band Needle
	needleX = (width / (radio_band_end - radio_band_start)) * (frequency - radio_band_start)
	draw.rectangle((needleX, 32, needleX+1, 22), fill=255)

def draw_alarm():
	global alarm_frame

	# Animation
	frame = Image.open('animations/alarm/frame-%s.png' % alarm_frame).resize((50, 30), Image.ANTIALIAS).convert('1')
	image.paste(frame, (int((width - 50) / 2), int((height - 30) / 2) - 5))
	if alarm_frame >= alarm_frame_max:
		alarm_frame = 0

	alarm_frame += 1

	# Clock
	draw.text(((width - 30) / 2, height/2+7), utils.get_time(), font=font, fill=255)

def home_mode_select_callback(index):
	global mode

	if index == 0:
		mode = 1
	elif index == 1:
		mode = 2

# Draw welcome screen
welcome_msg = "Welcome"
tmp = ""
for i in range(len(welcome_msg)):
	draw.rectangle((0,0,width,height), outline=0, fill=0)

	tmp = tmp + welcome_msg[i]
	draw.text(((width - 8*len(tmp)) / 2, height / 2), tmp, font=font, fill=255)

	disp.image(image)
	disp.display()
	time.sleep(.1)

time.sleep(1)

while True:
	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,width,height), outline=0, fill=0)

	confirm_state = GPIO.input(config["pins"]["confirm"])

	if sleep_timer <= 0:
		sleep=True
	else:
		sleep=False

	if GPIO.input(config["pins"]["confirm"]) == GPIO.HIGH:
		confirm_pressed +=1

		if confirm_pressed == 10:
			time.sleep(.1)
			mode = 0
	else:
		confirm_pressed = 0

	if not alarm_triggered and not sleep:
		draw_header()

		sleep_timer -= .1

		if mode == 0:
			entries = [
				"Radio",
				"Media",
				"Shutdown"
			]

			draw_menu("Mode", entries, home_mode_select_callback)

		elif mode == 1 and not in_menu:
			draw_radio(radio_frequency, True)

			if GPIO.input(config["pins"]["down"]) == GPIO.HIGH:
				if radio_frequency <= radio_band_end and radio_frequency >= radio_band_start:
					radio_frequency -= .5
				else:
					radio_frequency=radio_band_end

			if GPIO.input(config["pins"]["up"]) == GPIO.HIGH:
				if radio_frequency <= radio_band_end and radio_frequency >= radio_band_start:
                        		radio_frequency += .5
				else:
					radio_frequency=radio_band_start

		elif mode == 2 and not in_menu:
			mode = 0

	elif alarm_triggered:
		draw_alarm()
	elif sleep:
		pass

	# Display image.
	disp.image(image)
	disp.display()
	time.sleep(.1)

	confirm_last = confirm_state
