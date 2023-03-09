#!/usr/bin/python
# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import sys, os, time, datetime
import configparser
import socket
from datetime import datetime

#
# par Mathieu Légaré <levelkro@yahoo.ca>
#

config=False    
def loadConfig():
    global config
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    
def getConfig(value):
    global config
    try:
        return config['oled'][value]
    except:
        return ""
    
def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def getTimeNow():
    return datetime.datetime.timestamp(presentDate)*1000

def getFontFromType(id):
    global font1, font2, font3
    if int(id) == 1: return font1
    elif int(id) == 2: return font2
    elif int(id) == 3: return font3
    else: return False
    
def pasteText(txt):
    txt=txt.replace(":ipaddr:",getIP())
    return str(txt)
    
path=os.path.dirname(os.path.realpath(__file__))

loadConfig()
if(config['default']['oled']=="True"):
    from waveshare_OLED import OLED_0in91
    # Initialize library.
    disp = OLED_0in91.OLED_0in91()
    disp.Init()

    font1 = ImageFont.truetype(getConfig("font1_font"), int(getConfig("font1_size"))) # Main title
    font2 = ImageFont.truetype(getConfig("font2_font"), int(getConfig("font2_size"))) # Sub title
    font3 = ImageFont.truetype(getConfig("font3_font"), int(getConfig("font3_size"))) # Text

    mode="standby"
    standby_show=1
    standby_last=0
    oled_image = Image.new('1', (disp.width, disp.height), "WHITE")
    oled_draw = ImageDraw.Draw(oled_image) 
    while True:
        display=False
        for x in sorted(os.listdir("oled"), reverse=False):
            if x.endswith(".oled"):
                oled_draw.rectangle((0, 0,disp.width, disp.height), outline=255, fill=1)
                try:
                    display = configparser.ConfigParser()
                    display.read("oled/"+x, encoding='utf-8')
                    mode=display['info']['mode']
                    if(mode=="edit"):
                        oled_draw.rectangle((0, 0,disp.width, disp.height), outline=255, fill=1)
                        i=1         
                        while i<=int(display['info']['lines']):
                            oled_draw.text((int(display['line'+str(i)]['posx']),int(display['line'+str(i)]['posy'])), pasteText(display['line'+str(i)]['text']), font = getFontFromType(display['line'+str(i)]['type']), fill = 0)
                            i=int(i + 1)
                        #oled_image=oled_image.rotate(0)       
                        disp.ShowImage(disp.getbuffer(oled_image))
                        if(display['info']['mintime'] != "False" or display['info']['mintime'] != "0"):
                            time.sleep(int(display['info']['mintime']))
                    
                except:
                    print("Error with file "+str(x))
                os.remove("oled/"+x)
        if(mode=="standby" and int(datetime.now().timestamp() - standby_last) >= 10):
            oled_draw.rectangle((0, 0,disp.width, disp.height), outline=255, fill=1)
            if(standby_show==1):
                #Standby with custom display
                standby_show=2
                if(config['oled']['icon']!=""):
                    img = Image.open(config['oled']['icon'])
                    oled_image.paste(img, (int(config['oled']['icon_posx']),int(config['oled']['icon_posy'])))
                if(config['oled']['name']!=""):
                    oled_draw.text((int(config['oled']['name_posx']),int(config['oled']['name_posy'])),pasteText(config['oled']['name']), font=getFontFromType(int(config['oled']['name_type'])), fille=0)
                if(config['oled']['info1']!=""):
                    oled_draw.text((int(config['oled']['info1_posx']),int(config['oled']['info1_posy'])),pasteText(config['oled']['info1']), font=getFontFromType(int(config['oled']['info1_type'])), fille=0)
                if(config['oled']['info2']!=""):
                    oled_draw.text((int(config['oled']['info2_posx']),int(config['oled']['info2_posy'])),pasteText(config['oled']['info2']), font=getFontFromType(int(config['oled']['info2_type'])), fille=0)
            else:
                standby_show=1
                # Default image for standby, force "screensaver" effect
                img = Image.open("oled/oled_standby.jpg")
                oled_image.paste(img, (0,0))
            #oled_image=oled_image.rotate(0)      
            disp.ShowImage(disp.getbuffer(oled_image))
            standby_last=datetime.now().timestamp()

       
        
