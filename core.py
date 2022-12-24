from PIL import Image, ImageDraw, ImageFont
import getopt, sys, os, time, datetime
import treepoem, configparser
from datetime import datetime

#
# Étiquetteuse Brother-QL
# par Mathieu Légaré <levelkro@yahoo.ca>
#
# v1.2.1217
#

config=False    
def loadConfig():
    global config
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

def writeOLED(mode,lines=False,icon=False,mintime=0):
    saveconfig = configparser.ConfigParser()
    saveconfig['info']={}
    saveconfig['info']['mode']=str(mode)
    saveconfig['info']['mintime']=str(mintime)
    if(lines):
        x=1
        for line in lines:
            saveconfig['line'+str(x)]=line
            x=int(x + 1)
        saveconfig['info']['lines']=str(int(x - 1))
    else:
        saveconfig['info']['lines']="0"
    if(icon):
        saveconfig['info']['icon']=icon['file']
        saveconfig['info']['icon_posx']=icon['posx']
        saveconfig['info']['icon_posy']=icon['posy']
    else:
        saveconfig['info']['icon']="False"
    with open('oled/'+str(int(datetime.now().timestamp()))+'.oled', 'w', encoding='utf-8') as configfile:    # save
        saveconfig.write(configfile)

loadConfig()

bqlModel=config['printer']['model']
bqlUSB=config['printer']['usb']
bqlSerial=config['printer']['serial']

#Colors to use, Brother QL use Black only, some model RED' but not use it.
cWhite=(255,255,255)
cBlack=(0,0,0)

#Text values
fontName=config['default']['font_name']

#Output values
outWidth=int(config['default']['output_size_width'])
outHeight=int(config['default']['output_size_height'])
outFile=config['default']['output_file']

if(str(config['default']['debug'])=="True"):
    print("Debug Enabled")
    DEBUG=True
else:
    DEBUG=False

if(str(config['default']['oled'])=="True"):
    print("OLed Enabled")
    OLED=True
else:
    OLED=False
    
#Do not edit, default parameters
action=""

output=False
outputDraw=False
text=""
textcode=False
textsub=False
textinfo=False
image=False
option=False
direction=""
textpackage=config['expire']['text_package']
textexpire=config['expire']['text_expire']

copies=1

argv = sys.argv[1:]
opts, args = getopt.getopt(argv,"ha:t:s:n:c:i:d:r:k:v:")

for opt, arg in opts:
    if opt == '-h':
        print("*** Help of Image creator and print")
        print("Syntax: core.py -a <action> [parameters]")
        print("\t-a text")
        print("\t\t-t \"Text to print\"")
        print("\t-a textlarge")
        print("\t\t-t \"Text to print\"")
        print("\t-a textimage (require -t and -i)")
        print("\t\t-t \"Text to print\"")
        print("\t\t-i \"path/to/filename.jpg\" (support JPeg, PNG and GIF)")
        print("\t\t-r 1 [Optional] Enable \"textlarge\" style")
        print("\t-a cable")
        print("\t\t-t \"Text to print\"")
        print("\t-a address (require -n, -s or -c)")
        print("\t\t-t \"Name\" [Optional]")
        print("\t\t-n \"Street address\" [Optional]")
        print("\t\t-s \"City, State, Country\" [Optional]")
        print("\t\t-c \"P0ST4L/Z1P C0D3\" [Optional]")
        print("\t-a expire (require -n or -s)")
        print("\t\t-t \"Name\" [Optional]")
        print("\t\t-n \"00/00/00\" [Optional] Packaged date")
        print("\t\t-s \"00/00/00\" [Optional] Expiration date")
        print("\t-a barcode (require -c)")
        print("\t\t-t \"Name\" [Optional]")
        print("\t\t-c \"Text to encode\"")
        print("\t\t-r 1 [Optional] Enable sub text of barcode")
        print("\t\t-d \"left|top|right|bottom\" [Optional] Default is \"bottom\". Position of barcode (use with -t)")
        print("\t-a archive (require -c)")
        print("\t\t-t \"Name\" [Optional]")
        print("\t\t-t \"Owner information\" [Optional]")
        print("\t\t-c \"Text to encode\"")
        print("\t\t-r 1 [Optional] Enable sub text of barcode")
        sys.exit()
    elif opt in ("-a", "--action"):
        action = arg
    elif opt in ("-c", "--code"):
        textcode = arg
    elif opt in ("-t", "--text"):
        text = arg
    elif opt in ("-s", "--sub"):
        textsub = arg
    elif opt in ("-n", "--info"):
        textinfo = arg
    elif opt in ("-k", "--copies"):
        copies = int(arg)
    elif opt in ("-d", "--direction"):
        direction = arg
    elif opt in ("-r", "--option"):
        option = arg
    elif opt in ("-i", "--image"):
        image = arg
    elif opt in ("-v", "--verbose"):
        DEBUG=True

#Functions
def debug(text):
    if(DEBUG==True):
        print("*** "+text)

def oledshow(info,xtra="",noimg=False):
    if(OLED==True):
        try:
            if(noimg):
                noimg=' -x "1"'
            else:
                noimg=""
            if(info=="Ready!"):
                writeOLED("standby")
            else:
                writeOLED("edit",
                          [{"type":"1","posx":"0","posy":"0","text":"RPi-QL"},
                           {"type":"2","posx":"0","posy":"12","text":str(info)},
                           {"type":"3","posx":"0","posy":"23","text":str(xtra)}],
                          {"file":"logo.jpg","posx":"0","posy":"0"},3)
            #os.system('python3 oled.py -t "RPi-QL" -i "'+str(info)+'" -n "'+str(xtra)+'"'+noimg)
        except:
            print("Can't run OLED script")
        
def img_new(x=False,y=False):
    global config,output,outputDraw,outWidth,outHeight
    debug(" * Create Draw")
    if(x):
        globals()['outWidth']=int(x)
    if(y):
        globals()['outHeight']=int(y)
    debug(" * New draw with dimension of "+str(outWidth)+"x"+str(outHeight))
    output=Image.new('RGB', (outWidth, outHeight), color = cWhite)
    outputDraw=ImageDraw.Draw(output)
    debug(" * Draw created")

def img_text(x,y,size,text):
    global config,output,outputDraw
    fnt = ImageFont.truetype(fontName, size)
    debug(" * Drawing a text : "+str(text))
    outputDraw.text((x,y), str(text), font=fnt, fill=cBlack)

def img_image(x,y,file,r=False):
    global config,output,outputDraw
    debug(" * Open image : "+str(file))
    img = Image.open(file)
    if(r):
        debug(" * Resize image for "+str(r[0])+"x"+str(r[1]))
        img=img.resize(tuple(r))
    debug(" * Drawing image at "+str(x)+"x"+str(y))
    output.paste(img, (x,y))
    
def img_barcode_gen(code,file,encode="code128"):
    global config,output,outputDraw
    debug(" * Generating barcode image...")
    image = treepoem.generate_barcode(barcode_type=encode,data=code,)
    debug(" * Save the generated barcode into temporary file")
    image.convert("1").save(file)    
 
def img_barcode(file,w,h,x=0,y=0,r=False):
    global config,output,outputDraw
    debug(" * Open the barcode file : "+str(file))
    img = Image.open(file)
    if(r):
        debug(" ** Keep ratio of image barcode")
        if(h < w):
            img_ratio=img.height / h
        else:
            img_ratio=img.width / w
        img_w=int(img.width / img_ratio)
        img_h=int(img.height / img_ratio)
    else:
        debug(" ** Max width and height of image barcode (free resize) ")
        img_w=w
        img_h=h

    debug(" * Resize the barcode image to fit in the Draw ("+str(img_w)+"x"+str(img_h)+")")
    img=img.resize((int(img_w), int(img_h)))
    debug(" * Drawing the barcode at position "+str(x)+"x"+str(y))
    output.paste(img, (x,y))

def img_text_max(text,w=outWidth,h=outHeight,r=False):
    global config,output,outputDraw
    size=h
    tw=0
    debug(" * Finding the maximum height for the width of the Draw ("+str(w)+", size is "+str(size)+") ")
    while(tw > w or tw == 0):
        size = size - 1
        #debug(" * Test font size : "+str(size))
        fnt = ImageFont.truetype(fontName, size)
        tw=fnt.getbbox(text)[2]
        if(size<=0):
            print("Error : Text size is too small for use it (in others words, your text is too long for insert it in the image)")
            sys.exit(2)
    if(r=="h"):
        debug(" * Report the result of height : "+str(fnt.getbbox(text)[3])+" based on "+str(fnt.getbbox(text)))
        return fnt.getbbox(text)[3]
    elif(r=="w"):
        debug(" * Report the result of width : "+str(fnt.getbbox(text)[2])+" based on "+str(fnt.getbbox(text)))
        return fnt.getbbox(text)[2]
    else:
        debug(" * Report result of text font size to use : "+str(size))
        return int(size)
            
def img_image_dimension(file,s=False): 
    global config,output,outputDraw
    debug(" * Finding image sizes")
    with Image.open(file) as img:
        full = img.size
    if(s == "w"):
        debug(" * Report width")
        return full[0]
    elif(s == "h"):
        debug(" * Report height")
        return full[1]
    else:
        debug(" * Report default (full)")
        return full
            
def img_rotate(angle): 
    global config,output,outputDraw
    #img_save("temp_"+outFile)
    #output = Image.open("temp_"+outFile)
    debug("* Rotating draw for "+str(angle)+" degree")
    output=output.rotate(angle, expand=True) 

def img_save(file):
    global config,output,outputDraw
    debug(" * Save the draw")
    output.save(file)
            
def img_print():
    global config
    i=1
    debug("Printing  "+str(copies)+" copies")
    if(DEBUG!=True):
        oledshow("Label ready!","Printing...")
        while( i <= copies):
            debug(" * Printing copie #"+str(i))
            os.system('sudo brother_ql -m '+config['printer']['model']+' -p usb://'+config['printer']['usb']+'/'+config['printer']['serial']+' print '+outFile+' -l 62 --600dpi')
            #time.sleep(2)
            i+=1
    else:
        oledshow("Label ready!","No Print (DEBUG)...")
        debug(" * Printing result (disabled, DEBUG enabled)")
        
def img_clean(barcode=False):
    oledshow("Ready!","://:ipaddr::"+str(config['web']['port'])+"/")
    if(DEBUG!=True):
        try:
            if(barcode):
                os.remove("temp_"+outFile)
            os.remove(outFile)
        except:
            print("Can't delete created file(s)")
    else:
        debug(" * Cleaning files (disabled, DEBUG enabled)")

#Script of the app
if action == "text":
    # -a text -t "text"
    oledshow("Text label","Generating...")
    debug("Generate a text label")
    try:
        debug("Getting dimension of text")
        txt_w=img_text_max(text,outWidth,outHeight,"w")
        txt_h=img_text_max(text,outWidth,outHeight,"h")
        txt_f=img_text_max(text,outWidth,outHeight)
        debug("Creating the workspace")
        img_new(txt_w,txt_h) 
        debug("Adding text to draw") 
        img_text(0,0,txt_f,text)
        debug("Saving the file")
        img_save(outFile)
    except Exception as e:
        print("Error creating image")
        print(e)
        sys.exit(2)
    debug("Send to printer the result")
    img_print()
    debug("Cleaning")
    img_clean()
    
elif action == "cable":
    # -a cable -t "text"
    oledshow("Cable label","Generating...")
    try:
        debug("Getting dimension of text")
        sidetext=int((outWidth * 0.66) / 2)
        txt_w=img_text_max(text,sidetext,outHeight,"w")
        txt_h=img_text_max(text,sidetext,outHeight,"h")
        txt_f=img_text_max(text,sidetext,outHeight)
        debug("Generate the workspace")
        img_new(outWidth,txt_h)
        debug("Adding text to left")         
        img_text(0,0,txt_f,text)
        debug("Adding text to right")         
        img_text(int(outWidth - txt_w),0,txt_f,text)
        debug("Saving the file")
        img_save(outFile)
    except Exception as e:
        print("Error creating image")
        print(e)
        sys.exit(2)
    debug("Send to printer the result")
    img_print()
    debug("Cleaning")
    img_clean()
    
elif action == "textlarge":
    # -a textlarge -t "text"
    oledshow("Large text label","Generating...")
    debug("Generate a large text label")
    try:
        debug("Getting dimension of text")
        outWidth=int(len(text) * outHeight)
        #Warning, size of width is oversized, need to be rotated
        txt_w=img_text_max(text,outWidth,outHeight,"w")
        txt_h=img_text_max(text,outWidth,outHeight,"h")
        txt_f=img_text_max(text,outWidth,outHeight)
        debug("Creating the workspace")
        img_new(txt_w,txt_h) 
        debug("Adding text to draw") 
        img_text(0,0,txt_f,text)
        img_rotate(90)
        debug("Saving the file")
        img_save(outFile)
    except Exception as e:
        print("Error creating image")
        print(e)
        sys.exit(2)
    debug("Send to printer the result")
    img_print()
    debug("Cleaning")
    img_clean()
        
elif action == "textimage":
    # -a textimage -t "text" -i "path/imagename.ext" [-d "left|right" -r 1]
    oledshow("Text & Image label","Generating...")
    debug("Generate text label with image")
    try:
        #add option -r for rotate (large style)
        img_wmax=int(outWidth/5) # 20%
        debug("Getting dimension of image")
        imgsize=img_image_dimension(image)
        img_w=imgsize[0]
        img_h=imgsize[1]
        if(img_w>img_wmax):
            img_ratio=img_w / img_wmax
            img_w=int(img_w / img_ratio)
            img_h=int(img_h / img_ratio)
        if(img_h>outHeight):
            img_ratio=img_h / outHeight
            img_w=int(img_w / img_ratio)
            img_h=int(img_h / img_ratio)
        outHeight=img_h
        debug("Getting dimension of text")
        txt_w=img_text_max(text,int(outWidth - 10 - img_w),outHeight,"w")
        txt_h=img_text_max(text,int(outWidth - 10 - img_w),outHeight,"h")
        txt_f=img_text_max(text,int(outWidth - 10 - img_w),outHeight)
        if(direction=="right"):
            img_marge=int(outWidth - img_w)
            txt_marge=0
        else:
            img_marge=0
            txt_marge=int(10 + img_w)
        if(img_h<txt_h):
            img_top=int((txt_h - img_h) / 2)
            outHeight=txt_h
        else:
            img_top=0
        if(txt_h<img_h):
            txt_top=int((img_h - txt_h) / 2)
        else:
            txt_top=0
        debug("Creating the workspace")
        img_new()          
        debug("Adding image to draw") 
        img_image(img_marge,img_top,image,(img_w,img_h)) 
        debug("Adding text to draw") 
        img_text(txt_marge,txt_top,txt_f,text)
        debug("Saving the file")
        img_save(outFile)
    except Exception as e:
        print("Error creating image")
        print(e)
        sys.exit(2)
    debug("Send to printer the result")
    img_print()
    debug("Cleaning")
    img_clean()
    
elif action == "address":
    # -a address -t "name" -s "street address" -n "city, state, country" -c "postal code"
    oledshow("Address label","Generating...")
    debug("Generate address label")
    try:
        lines=0
        line_top=0
        if(text!=""):
            lines=int(lines + 1)
        if(textsub):
            lines=int(lines + 1)
        if(textinfo):
            lines=int(lines + 1)
        if(textcode):
            lines=int(lines + 1)
        line_h=int((outHeight / lines) - ((lines - 1) * 2))
        debug("Generate the workspace")
        img_new()
        debug("Getting dimension of text and adding it to draw")
        if(text!=""):
            txt_w=img_text_max(text,outWidth,line_h,"w")
            txt_h=img_text_max(text,outWidth,line_h,"h")
            txt_f=img_text_max(text,outWidth,line_h)
            debug("Adding text to draw") 
            img_text(0,line_top,txt_f,text)
            line_top=int(line_top + 2 + txt_h)
        if(textinfo is not False):
            txt_w=img_text_max(textinfo,outWidth,line_h,"w")
            txt_h=img_text_max(textinfo,outWidth,line_h,"h")
            txt_f=img_text_max(textinfo,outWidth,line_h)
            debug("Adding text to draw") 
            img_text(0,line_top,txt_f,textinfo)
            line_top=int(line_top + 2 + txt_h)
        if(textsub is not False):
            txt_w=img_text_max(textsub,outWidth,line_h,"w")
            txt_h=img_text_max(textsub,outWidth,line_h,"h")
            txt_f=img_text_max(textsub,outWidth,line_h)
            debug("Adding text to draw")
            img_text(0,line_top,txt_f,textsub)
            line_top=int(line_top + 2 + txt_h)
        if(textcode is not False):
            txt_w=img_text_max(textcode,outWidth,line_h,"w")
            txt_h=img_text_max(textcode,outWidth,line_h,"h")
            txt_f=img_text_max(textcode,outWidth,line_h)
            debug("Adding text to draw")
            img_text(0,line_top,txt_f,textcode)
        debug("Saving the file")
        img_save(outFile)   
    except Exception as e:
        print("Error creating image")
        print(e)
        sys.exit(2)
    debug("Send to printer the result")
    img_print()
    debug("Cleaning")
    img_clean()
    
elif action == "expire":
    oledshow("Expiration label","Generating...")
    #-a expire -t "name" -p "00/00/00" -e "00/00/00"
    debug("Generate 'best before' label")
    try:
        draw_h=0
        outHalfWidth=int((outWidth / 2) - 10)
        outHalfHeight=int((outHeight / 2) - 10)
        outQuarterHeight=int((outHeight / 4) - 5)
        if(text!=""):
            txt_w=img_text_max(text,outWidth,outHalfHeight,"w")
            txt_h=img_text_max(text,outWidth,outHalfHeight,"h")
            txt_f=img_text_max(text,outWidth,outHalfHeight)
            draw_h=(draw_h + txt_h + 10)
        if(textinfo):
            info_w=img_text_max(textinfo,outHalfWidth,outHalfHeight,"w")
            info_h=img_text_max(textinfo,outHalfWidth,outHalfHeight,"h")
            info_f=img_text_max(textinfo,outHalfWidth,outHalfHeight)
            info_top=draw_h
            draw_h=int(draw_h + info_h + 5)
            info_marge=int(outWidth - info_w)
        if(textsub):
            sub_w=img_text_max(textsub,outHalfWidth,outHalfHeight,"w")
            sub_h=img_text_max(textsub,outHalfWidth,outHalfHeight,"h")
            sub_f=img_text_max(textsub,outHalfWidth,outHalfHeight)
            sub_top=draw_h
            sub_marge=int(outWidth - sub_w)
            draw_h=int(draw_h + sub_h + 5)
        debug("Generate the workspace")
        img_new(outWidth,draw_h)
        if(text!=""):
            if(txt_w<outWidth):
                txt_marge=int((outWidth - txt_w) / 2)
            else:
                txt_marge=0
            debug("Adding text to draw")
            img_text(txt_marge,0,txt_f,text)
        if(textinfo):
            debug("Adding text to draw")
            img_text(0,info_top,info_f,textpackage)
            img_text(info_marge,info_top,info_f,textinfo)
        if(textsub):
            debug("Adding text to draw")
            img_text(0,sub_top,sub_f,textexpire)
            img_text(sub_marge,sub_top,sub_f,textsub)
        debug("Saving the file")
        img_save(outFile)  
    except Exception as e:
        print("Error creating image")
        print(e)
        sys.exit(2)
    debug("Send to printer the result")
    img_print()
    debug("Cleaning")
    img_clean()
    
elif action == "barcode":
    #-a barcode -t "text" -c "code" [-d "left|top|right|bottom(default)"]
    oledshow("Barcode label","Generating...")
    debug("Generate a barcode label")
    try:
        outHalfWidth=int((outWidth / 2) - 10)
        outHalfHeight=int((outHeight / 2) - 10)
        debug("Generate the barcode")
        img_barcode_gen(str(textcode),"temp_"+outFile)
        bar_h=outHeight
        bar_w=outWidth
        bar_marge=0
        bar_top=0
        txt_top=0
        txt_marge=0
        if(text!=""):
            bar_h=outHalfHeight
            if(direction=="left" or direction=="right"):
                txt_w=img_text_max(text,outHalfWidth,outHeight,"w")
                txt_h=img_text_max(text,outHalfWidth,outHeight,"h")
                txt_f=img_text_max(text,outHalfWidth,outHeight)
                bar_w=outHalfWidth
                bar_top=10
                if(direction=="right"):
                    bar_marge=int(outHalfWidth + 5)
                else:
                    txt_marge=int(outWidth - txt_w)
                outHeight=txt_h
            else:
                txt_w=img_text_max(text,outWidth,outHalfHeight,"w")
                txt_h=img_text_max(text,outWidth,outHalfHeight,"h")
                txt_f=img_text_max(text,outWidth,outHalfHeight)
                if(direction=="top"):
                    txt_top=int(outHalfHeight + 10)
                else:
                    bar_top=int(outHalfHeight + 10)
                if(txt_w<outWidth):
                    txt_marge=int((outWidth - txt_w) / 2)

        debug("Generate the workspace")
        img_new()
        if(option!=False):
            bar_h=int(outHalfHeight - 30)
        debug("Adding barcode image to draw")       
        img_barcode("temp_"+outFile,bar_w,bar_h,bar_marge,bar_top)
        if(option!=False):
            code_w=img_text_max(textcode,outWidth,30,"w")
            code_h=img_text_max(textcode,outWidth,30,"h")
            code_f=img_text_max(textcode,outWidth,30)
            code_marge=int((outWidth - code_w) / 2 )
            code_top=int(bar_top + bar_h)
            debug("Adding text to draw")
            img_text(code_marge,code_top,code_f,textcode)
        if(text!=""):
            debug("Adding text to draw")
            img_text(txt_marge,txt_top,txt_f,text)
        debug("Saving the file")
        img_save(outFile)
    except Exception as e:
        print("Error creating image")
        print(e)
        sys.exit(2)
    debug("Send to printer the result")
    img_print()
    debug("Cleaning")
    img_clean(True)
    
elif action == "archive":
    #-a barcode -t "text" -c "code" [-d "left|top|right|bottom(default)"]
    oledshow("Archive label","Generating...")
    debug("Generate archiving label (text with barcode, with display code forced)")
    debug("The barcode is at down of label")
    try:
        outHalfWidth=int((outWidth / 2) - 10)
        outHalfHeight=int((outHeight / 2) - 10)
        outFiveHeight=int((outHeight / 5) - 10)
        debug("Generate the barcode")
        img_barcode_gen(str(textcode),"temp_"+outFile)
        line_pos=0
        bar_w=int(outWidth / 2)
        bar_top=0
        bar_marge=int((outWidth - bar_w) / 2)
        bar_h=outHalfHeight
        if(text!=""):
            bar_h=outHalfHeight
            if(textinfo):
                info_top=int(outHalfHeight - outFiveHeight)
                txt_w=img_text_max(text,outWidth,info_top,"w")
                txt_h=img_text_max(text,outWidth,info_top,"h")
                txt_f=img_text_max(text,outWidth,info_top)
                info_w=img_text_max(textinfo,outWidth,outFiveHeight,"w")
                info_h=img_text_max(textinfo,outWidth,outFiveHeight,"h")
                info_f=img_text_max(textinfo,outWidth,outFiveHeight)
                info_top=int(info_top + 5)
                bar_top=int(bar_top + txt_h + info_h + 10)
                if(info_w<outWidth):
                    info_marge=int((outWidth - info_w) / 2)
                else:
                    info_marge=0
            else:
                bar_top=int(bar_top + txt_h + 10)
                txt_w=img_text_max(text,outWidth,outHalfHeight,"w")
                txt_h=img_text_max(text,outWidth,outHalfHeight,"h")
                txt_f=img_text_max(text,outWidth,outHalfHeight)
            txt_top=0
            if(txt_w<outWidth):
                txt_marge=int((outWidth - txt_w) / 2)
            else:
                text_marge=0
        elif(textinfo):
            info_top=0
            info_w=img_text_max(textinfo,outWidth,outFiveHeight,"w")
            info_h=img_text_max(textinfo,outWidth,outFiveHeight,"h")
            info_f=img_text_max(textinfo,outWidth,outFiveHeight)
            if(info_w<outWidth):
                info_marge=int((outWidth - info_w) / 2)
            else:
                info_marge=0
            bar_top=int(info_h + 10)
        outHeight=int(bar_top + bar_h + 5)
        bar_h=int(bar_h - 30)            
        debug("Generate the workspace")
        img_new()
        debug("Adding barcode image to draw")       
        img_barcode("temp_"+outFile,bar_w,bar_h,bar_marge,bar_top)
        code_w=img_text_max(textcode,outWidth,30,"w")
        code_h=img_text_max(textcode,outWidth,30,"h")
        code_f=img_text_max(textcode,outWidth,30)
        code_marge=int((outWidth - code_w) / 2 )
        code_top=int(bar_top + bar_h)
        debug("Adding text to draw")
        img_text(code_marge,code_top,code_f,textcode)
        if(text!=""):
            debug("Adding text to draw")
            img_text(txt_marge,txt_top,txt_f,text)
        if(textinfo):
            debug("Adding text to draw")
            img_text(info_marge,info_top,info_f,textinfo)
        debug("Saving the file")
        img_save(outFile)
    except Exception as e:
        print("Error creating image")
        print(e)
        sys.exit(2)
    debug("Send to printer the result")
    img_print()
    debug("Cleaning")
    img_clean(True)
else:
    print("Error : Action "+action+" is not valid")

sys.exit()


