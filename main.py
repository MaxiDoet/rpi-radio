import RPi.GPIO as GPIO
import json
from log import *
import time
import subprocess

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

# Menu variables
in_menu = True
menu_index = 0
menu_index_max = 1
menu_title = "Radio"

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

def button_up_event(channel):
	debug("button up event")
	if in_menu:
		if menu_index is 0:
			menu_index = menu_index_max
		else:
			menu_index -= 1

def button_down_event(channel):
	debug("button down event")
	if in_menu:
		if menu_index is menu_index_max:
			menu_index = 0
		else:
			menu_index += 1

def button_confirm_event(channel):
	debug("button confirm event")

#GPIO.add_event_detect(config["pins"]["up"],GPIO.RISING,callback=button_up_event)
#GPIO.add_event_detect(config["pins"]["down"],GPIO.RISING,callback=button_down_event)
#GPIO.add_event_detect(config["pins"]["confirm"],GPIO.RISING,callback=button_confirm_event)

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

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

radio_frequency = 100

def draw_screen_radio(frequency):
	# Menu title
	draw.text(((width - 8*len(menu_title)) / 2, top), menu_title, font=font, fill=255)

	# Clock
	draw.text(((width - 30), top), "13:54", font=font, fill=255)

	# Seperator
	draw.line((0, 8, width, 8), fill=255)

	# Frequency
	draw.text(((width - 8*len("%shz" % frequency)) / 2, height/2-5), "%shz" % frequency, font=font, fill=255)

	# Stereo indicator
	#stereo = Image.open('stereo.png').resize((10, 7), Image.ANTIALIAS).convert('1')
	#image.paste(stereo, (0, 1))
	draw.text((1, top), "S", font=font, fill=255)

	# Band
	band = Image.open('band.png').resize((128, 8), Image.ANTIALIAS).convert('1')
	image.paste(band, (0, 32-8))

	# Band Needle
	needleX = (width / (108 - 87.5)) * (frequency - 87.5)
	draw.rectangle((needleX, 32, needleX+1, 22), fill=255)

while True:
	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,width,height), outline=0, fill=0)

	draw_screen_radio(radio_frequency)

	# Display image.
	disp.image(image)
	disp.display()
	time.sleep(.1)

	if GPIO.input(18) == GPIO.HIGH:
		if radio_frequency <= 108 and radio_frequency >= 87.5:
			radio_frequency += .5
		else:
			radio_frequency=87.5
