#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import logging    
import time
import traceback
import getopt
from waveshare_OLED import OLED_0in91
from PIL import Image,ImageDraw,ImageFont
#logging.basicConfig(level=logging.DEBUG)

import socket   
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IPAddr=s.getsockname()[0]
path=os.path.dirname(os.path.realpath(__file__))

argv = sys.argv[1:]

opts, args = getopt.getopt(argv,"h:t:i:n:x:")

out_title="RPi-QL"
out_info=""
out_xtra=""
out_noimg=False

for opt, arg in opts:
    if opt == '-h':
        print("*** Help of OLED 0.91 Display")
        print('Syntax: oled.py -t "title text" -i "info text" -n "extra info text"')
        
        sys.exit()
    elif opt in ("-t"):
        out_title = arg
    elif opt in ("-i"):
        out_info = arg.replace(":ipaddr:",IPAddr)
    elif opt in ("-n"):
        out_xtra = arg.replace(":ipaddr:",IPAddr)
    elif opt in ("-x"):
        out_noimg = True
    else:
        print("Found: "+str(opt))


disp = OLED_0in91.OLED_0in91()
# Initialize library.
disp.Init()

# Clear display.
disp.clear()

# Create blank image for drawing.
image1 = Image.new('1', (disp.width, disp.height), "WHITE")
draw = ImageDraw.Draw(image1)
font1 = ImageFont.truetype("DejaVuSansMono.ttf", 12)
font2 = ImageFont.truetype("DejaVuSansMono.ttf", 11)
font3 = ImageFont.truetype("DejaVuSansMono.ttf", 9)

if(out_noimg):
    draw.text((0,0), out_title, font = font1, fill = 0)
    draw.text((2,12), out_info, font = font2, fill = 0)
    draw.text((2,23), out_xtra, font = font3, fill = 0)
else:
    img = Image.open(path+"/logo.jpg")
    image1.paste(img, (0,0))
    draw.text((32,0), out_title, font = font1, fill = 0)
    draw.text((33,12), out_info, font = font2, fill = 0)
    draw.text((33,23), out_xtra, font = font3, fill = 0)
    image1=image1.rotate(0) 

disp.ShowImage(disp.getbuffer(image1))
