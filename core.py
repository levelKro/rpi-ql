from PIL import Image, ImageDraw, ImageFont
import getopt, sys, os, time
import treepoem, configparser

#
# Étiquetteuse Brother-QL
# par Mathieu Légaré <levelkro@yahoo.ca>
#
# v1.2.1106
#
config=False    
def loadConfig():
    global config
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    
loadConfig()

bqlModel=config['printer']['model']
bqlUSB=config['printer']['usb']
bqlSerial=config['printer']['serial']

#Colors to use, Brother QL use Black only, some model RED' but not use it.
#add negative
cWhite=(255,255,255)
cBlack=(0,0,0)

#Text values
fontName=config['default']['font_name']
textSize=int(config['default']['font_size'])
textSizeSmall=int(config['default']['font_size_small'])

#Cable action space to remove for the "cable" roll
cableCenter=int(config['cable']['center'])

#Output values
outWidth=int(config['default']['output_size_width'])
outHeight=int(config['default']['output_size_height'])
outFile=config['default']['output_file']
outImageMaxRatio=float(config['textimage']['max_image'])

#Barcode action, size compared of total of the created image
barcodeRatio=float(config['barcode']['height'])
print("Debug:"+str(config['default']['debug']))
if(str(config['default']['debug'])=="True"):
    print("Debug Enabled")
    DEBUG=True
else:
    print("Print mode")
    DEBUG=False

#Do not edit, default parameters
action=""

TEXT_PACKIN="Emballé le"
TEXT_EXPIRE="Expire le"

output=False
outputDraw=False
text=""
code=False
sub=False
owner=False
image=False

copies=1

poscode="10,10"
postext="10,10"
direction="down"
maxwidth=False
maxheight=False
marge=10
resizemode="wide"
#posimage="left"

argv = sys.argv[1:]

opts, args = getopt.getopt(argv,"ha:o:c:t:s:d:i:m:n:x:y:k:v:")

for opt, arg in opts:
    if opt == '-h':
        print("*** Help of Image creator and print")
        print("Syntax: core.py -a <action> [parameters]")
        print("-a\tAction")
        print("\t\tValues : text,textlarge,textimage,cable,expire,barcode,archive,address")
        print("-k\t(optional) Nomber of copie, default is 1")
        print("-t\tText/Title")
        print("\t\taction: text,textlarge,textimage,cable,expire,barcode,archive")
        print("\t\t\tTitle text for the label")
        print("\t\taction: address (optional)")
        print("\t\t\tName text for the address")
        print("-c\tCode/Postal code")
        print("\t\taction: barcode,archive")
        print("\t\t\tText to encode into barcode")
        print("\t\taction: address")
        print("\t\t\tPostal code of the address")
        print("-s\tSub-title/Expired date/Country and region text")
        print("\t\taction: barcode (optional)")
        print("\t\t\tAdd text under the barcode")
        print("\t\taction: expire (optional)")
        print("\t\t\tThe expired date")
        print("\t\taction: address")
        print("\t\t\tThe City,Region,Country text for address")
        print("-n\tOwner text/Packaged date,Civic")
        print("\t\taction: archive")
        print("\t\t\tThe subtitle/owner text uner the Title text")
        print("\t\taction: expire (optional)")
        print("\t\t\tThe date packaged")
        print("\t\taction: address")
        print("\t\t\tThe civic and street text")
        print("-i\tImage filename")
        print("\t\taction: textimage, image")
        print("\t\t\tThe selected image to add")
        print("-d\t(optional) Direction")
        print("\t\taction: barcode")
        print("\t\tvalues: up, down (default)")
        print("\t\t\tSet the barcode to up or down")
        print("\t\taction: textimage")
        print("\t\tvalues: right, left (default)")
        print("\t\t\tSet the image at left or right")
        print("-x\t(optional) Width")
        print("\t\taction: textimage")
        print("\t\t\tMax width of the image")
        print("-y\t(optional) Height")
        print("\t\taction: textimage")
        print("\t\t\tMax height of the image")
        print("-r\t(optional) Resize mode")
        print("\t\taction: textimage")
        print("\t\tvalues: portrait, wide (default)")
        print("\t\t\tResize by the max height (portrait) or max width (wide)")
        print("-m\t(optional) Marging")
        print("\t\taction: all")
        print("\t\t\tChange the deaulf marging value")
        print("-v\t(optional) Verbose")
        print("\t\tvalue: 1")
        print("\t\t\tTurn debug mode 1 and be Verbose")
            
        
        
        
        sys.exit()
    elif opt in ("-a", "--action"):
        action = arg
    elif opt in ("-o", "--output"):
        outFile = arg
    elif opt in ("-c", "--code"):
        code = arg
    elif opt in ("-t", "--text"):
        text = arg
    elif opt in ("-s", "--sub"):
        sub = arg
    elif opt in ("-n", "--owner"):
        owner = arg
    elif opt in ("-k", "--copies"):
        copies = int(arg)
    elif opt in ("-d", "--direction"):
        direction = arg
    elif opt in ("-x", "--maxwidth"):
        maxwidth = int(arg)
    elif opt in ("-y", "--maxheight"):
        maxheight = int(arg)
    elif opt in ("-r", "--resize"):
        resizemode = arg
    elif opt in ("-i", "--image"):
        image = arg
    #elif opt in ("-j", "--positionimage"):
    #    posimage = arg
    #elif opt in ("-m", "--marge"):
    #    marge = int(arg)
    #elif opt in ("-q", "--positioncode"):
    #    poscode = arg
    #elif opt in ("-u", "--positiontext"):
    #    postext = arg
    elif opt in ("-v", "--verbose"):
        DEBUG=True

#Functions
def debug(text):
    if(DEBUG==True):
        print("*** "+text)
        
def img_new(x=False,y=False):
    global config,output,outputDraw,outWidth,outHeight
    debug(" * Create Draw")
    if(x):
        globals()['outWidth']=int(x)
    if(y):
        globals()['outHeight']=int(y)
    debug(" * New image with "+str(outWidth)+"x"+str(outHeight))
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
    
def img_barcode_gen(code,file):
    global config,output,outputDraw
    debug(" * Generating barcode image...")
    image = treepoem.generate_barcode(barcode_type="code128",data=code,)
    debug(" * Save the generated barcode into temporary file")
    image.convert("1").save(file)    
 
def img_barcode(file,scode=False,x=marge,y=marge,r=False):
    global config,output,outputDraw
    debug(" * Open the barcode file : "+str(file))
    img = Image.open(file)
    if(r):
        debug(" ** Keep ratio of image barcodet")
        img_ratio=img.height / (outHeight / 2)
        img_w=int(img.width / img_ratio)
        img_h=int(img.height / img_ratio)
    else:
        debug(" ** Max width and height of image barcode (expand) ")
        img_w=int(outWidth - (x * 2))
        img_h=int((outHeight * barcodeRatio)  - (marge * 2))

    debug(" * Image dimension is ("+str(img_w)+"x"+str(img_h)+")")        
    if(scode is not False):
        fnt = ImageFont.truetype(fontName, textSizeSmall)
        th=fnt.getbbox(str(scode))[3]
        tw=fnt.getbbox(str(scode))[2]
        img_h=int(img_h - (th + 4))
        sy=int(y + img_h + 4)
        sx=(outWidth - tw) / 2
        if(sx <0):
            sx=0
        debug(" * Adding the sub text : "+str(scode))
        img_text(int(sx),int(sy),textSizeSmall,str(scode))
    debug(" * Resize the barcode image to fit in the Draw ("+str(img_w)+"x"+str(img_h)+")")
    img=img.resize((int(img_w), int(img_h)))
    debug(" * Drawing the barcode at position "+str(x)+"x"+str(y))
    output.paste(img, (x,y))

def img_text_fit(text,x=marge,y=marge,w=outWidth,h=outHeight):
    global config,output,outputDraw
    size = img_text_max(text,w,h)
    fnt = ImageFont.truetype(fontName, size)
    #x = int((h - size ) / 2)
    debug(" * Put text into "+str(x)+","+str(y)+" with text '"+text+"', fit into "+str(w)+" and "+str(h))
    outputDraw.text((x,y), text, font=fnt, fill=cBlack)
        
def img_text_max(text,w=outWidth,h=int(outHeight * 0.5),r=False):
    global config,output,outputDraw
    size=h + 1
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
        while( i <= copies):
            debug(" * Printing copie #"+str(i))
            os.system('sudo brother_ql -m '+config['printer']['model']+' -p usb://'+config['printer']['usb']+'/'+config['printer']['serial']+' print '+outFile+' -l 62 --600dpi')
            #time.sleep(2)
            i+=1
    else:
        debug(" * Printing result (disabled, DEBUG enabled)")
        
def img_clean(barcode=False):
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
if action == "barcode":
    debug("Generate a barcode label")
    #-c -t -s (-q -u) -d 
    if(direction=="up"):
        debug("Barcode is on the top of label")
        bs=[marge,marge]
        ts=[marge,int((outHeight / 2) + marge)]
    elif(direction=="down"):
        debug("The barcode is at down of label")
        ts=[marge,marge]
        bs=[marge,int((outHeight / 2) + marge)]
    else:
        debug("Use custom position")
        ts=postext.split(",")
        bs=poscode.split(",")
    try:
        debug("Generate the workspace")
        img_new()
        debug("Adding text")
        img_text_fit(text,int(ts[0]),int(ts[1]),int(outWidth - (2 * int(ts[0]))),int((outHeight / 2) - (2 * int(marge))))
        debug("Generate the barcode")
        if(code  is not False):
            img_barcode_gen(str(code),"temp_"+outFile)
            if(sub is not False):
                debug("Adding barcode with size for the sub text")
                img_barcode("temp_"+outFile,str(sub),int(bs[0]),int(bs[1]))
            else:
                debug("Adding barcode with normal size")
                img_barcode("temp_"+outFile,False,int(bs[0]),int(bs[1]))
        else:
            print("Error, code is missing")
            sys.exit(2)
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
    
elif action == "text":
    #-t -m
    debug("Generate a text label")
    try:
        debug("Creating the workspace")
        th=int(img_text_max(text,outWidth,int(outHeight * 2),"h") + (2 * marge))
        img_new(outWidth,th) 
        debug("Adding text to fit the space") 
        img_text_fit(text,marge,marge,int(outWidth - (2 * marge)),th)
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
    debug("Generate a large text label\r Text: "+str(text))
    try:
        debug("Creating the workspace")
        #Warning!!! WIDTH is HEIGHT and WIDTH is WIDTH here, the result was rotated
        debug("Shearching ideal size font for banner of maximum "+str((outWidth * 100))+"x"+str(outWidth))
        tw=int(img_text_max(text,(outWidth * 100),(outWidth - marge),"w"))
        th=int(img_text_max(text,(outWidth * 100),(outWidth - marge),"h"))
        debug("Creating new image with "+str(tw + (2 * marge))+"x"+str(th + (4 * marge))) 
        img_new(int(tw + (2 * marge)),int(th + (10 * marge))) 
        debug("Adding text to fit the space") 
        img_text_fit(text,marge,marge,tw,th)
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
    #-t -i -j (left|right) -x -y -m -w 
    debug("Generate text label with image")
    imgsize=img_image_dimension(image)
    imgwidth=imgsize[0]
    imgheight=imgsize[1]
    if(maxwidth or maxheight):
        resize=True
        if(resizemode=="portrait"):
            if(maxheight and imgsize[1] != maxheight):
                ratio=maxheight / imgsize[1]
                imgwidth=int(imgsize[0] * ratio)
                imgheight=int(imgsize[1] * ratio)
            if(maxwidth and imgwidth > maxwidth):
                ratio=maxwidth / imgsize[0]
                imgwidth=int(imgsize[0] * ratio)
                imgheight=int(imgsize[1] * ratio)
        else:
            if(maxwidth and imgsize[0] != maxwidth):
                ratio=maxwidth / imgsize[0]
                imgwidth=int(imgsize[0] * ratio)
                imgheight=int(imgsize[1] * ratio)
            if(maxheight and imgheight > maxheight):
                ratio=maxheight / imgsize[1]
                imgwidth=int(imgsize[0] * ratio)
                imgheight=int(imgsize[1] * ratio)
    else:
        imgwidth=imgsize[0]
        imgheight=imgsize[1]
        
    if(imgwidth > (outWidth * outImageMaxRatio )):
        imgwidth=int(imgsize[0] * outImageMaxRatio)
        imgheight=int(imgsize[1] * outImageMaxRatio)
        
    if(imgheight>int(outHeight - (2 * marge))):
        ratio=float((outHeight - (2 * marge)) / imgsize[1])
        imgwidth=int(imgsize[0] * ratio)
        imgheight=int(imgsize[1] * ratio)
        
    if(direction=="right"):
        ix=int(outWidth - (marge + imgwidth))
        tx=marge
    else:
        ix=marge
        tx=int((2 * marge) + imgwidth)
        
    try:        
        tw=int(outWidth - ((2 * marge) + imgwidth))
        debug("Generate the workspace")
        img_new(outWidth,int(imgheight  + (2 * marge)))
        debug("Adding text to fit the space")
        ty=int((outHeight - img_text_max(text,tw,imgheight,"h")) / 2)
        img_text_fit(text,tx,ty,tw,imgheight)         
        debug("Adding image") 
        img_image(ix,marge,image,(imgwidth,imgheight)) 
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
    #-t -p (packaged) -e (expire)
    debug("Generate 'best before' label")
    hh=int(outHeight / 2) - marge
    hq=int(hh / 2)
    wh=int(outWidth / 2) - marge
    if(text != "" and owner is not False and sub is not False):
        debug("Working for '"+text+"' packed the '"+owner+"' expire the '"+sub+"'.")
        ptw=img_text_max(TEXT_PACKIN,wh,hq,"w")
        ptm=int(wh - ptw)
        etw=img_text_max(TEXT_EXPIRE,wh,hq,"w")
        etm=int(wh - etw)
        pw=img_text_max(owner,wh,hq,"w")
        ew=img_text_max(sub,wh,hq,"w")
        img_new() 
        img_text_fit(text,marge,0,outWidth,hh)
        img_text_fit(TEXT_PACKIN,ptm,int(hh)+marge,ptw,hq)
        img_text_fit(TEXT_EXPIRE,etm,int(hh + hq)+marge,etw,hq)
        img_text_fit(owner,int(wh + marge),int(hh)+marge,wh,hq)
        img_text_fit(sub,int(wh + marge),int(hh + hq)+marge,wh,hq) 
    elif(text != "" and owner is not False):
        debug("Working for '"+text+"' packed the '"+owner+"'.")
        ptw=img_text_max(TEXT_PACKIN,wh,hh,"w")
        pth=img_text_max(TEXT_PACKIN,wh,hh,"h")
        ptm=int(wh - ptw)
        pw=img_text_max(owner,wh,pth,"w")
        ph=img_text_max(owner,wh,pth,"h")
        if(pth>ph):
            th=ph
        elif(ph>pth):
            th=pth
        img_new() 
        img_text_fit(text,marge,0,outWidth,hh)
        img_text_fit(TEXT_PACKIN,ptm,int(hh)+marge,ptw,th)
        img_text_fit(owner,int(wh + marge),int(hh)+marge,pw,th)
    elif(text != "" and sub is not False):
        debug("Working for '"+text+"' expire the '"+sub+"'.")
        etw=img_text_max(TEXT_EXPIRE,wh,hh,"w")
        eth=img_text_max(TEXT_EXPIRE,wh,hh,"h")
        etm=int(wh - etw)
        debug("Print '"+sub+"' width:"+str(wh)+" height:"+str(eth))
        pw=img_text_max(sub,wh,eth,"w")
        ph=img_text_max(sub,wh,eth,"h")
        if(eth>ph):
            th=ph
        elif(ph>eth):
            th=eth
        img_new() 
        img_text_fit(text,marge,0,outWidth,hh)
        img_text_fit(TEXT_EXPIRE,etm,int(hh)+marge,etw,th)
        img_text_fit(sub,int(wh + marge),int(hh)+marge,pw,th)
    elif(owner is not False and sub is not False):
        debug("Working for packed the '"+owner+"' expire the '"+sub+"'.")
        ptw=img_text_max(TEXT_PACKIN,wh,hh,"w")
        pth=img_text_max(TEXT_PACKIN,wh,hh,"h")
        ptm=int(wh - ptw)
        etw=img_text_max(TEXT_EXPIRE,wh,hh,"w")
        eth=img_text_max(TEXT_EXPIRE,wh,hh,"h")
        etm=int(wh - etw)
        pw=img_text_max(owner,wh,hh,"w")
        ph=img_text_max(owner,wh,hh,"h")
        ew=img_text_max(sub,wh,hh,"w")
        eh=img_text_max(sub,wh,hh,"h")
        if(eth>eh):
            exth=eh
        elif(eh>eth):
            exth=eth
        if(pth>ph):
            pkth=ph
        elif(ph>pth):
            pkth=pth
        img_new() 
        img_text_fit(TEXT_PACKIN,ptm,marge,ptw,pkth)
        img_text_fit(owner,int(wh + marge),marge,wh,pkth)
        img_text_fit(TEXT_EXPIRE,etm,hh + marge,etw,exth)
        img_text_fit(sub,int(wh + marge),hh + marge,wh,exth)
    elif(owner is not False):
        debug("Working for packed the '"+owner+"'.")
        hh=int(outHeight - marge)
        ptw=img_text_max(TEXT_PACKIN,wh,hh,"w")
        pth=img_text_max(TEXT_PACKIN,wh,hh,"h")
        ptm=int(wh - ptw)
        pw=img_text_max(owner,wh,hh,"w")
        ph=img_text_max(owner,wh,hh,"h")
        if(pth>ph):
            pkth=ph
        elif(ph>pth):
            pkth=pth
        img_new(outWidth,int(marge + pkth)) 
        img_text_fit(TEXT_PACKIN,ptm,marge,ptw,pkth)
        img_text_fit(owner,int(wh + marge),marge,wh,pkth)
    elif(sub is not False):
        debug("Working for expire the '"+sub+"'.")
        hh=int(outHeight - marge)
        etw=img_text_max(TEXT_EXPIRE,wh,hh,"w")
        eth=img_text_max(TEXT_EXPIRE,wh,hh,"h")
        etm=int(wh - etw)
        ew=img_text_max(sub,wh,hh,"w")
        eh=img_text_max(sub,wh,hh,"h")
        if(eth>eh):
            exth=eh
        elif(eh>eth):
            exth=eth
        img_new(outWidth,int(marge + exth)) 
        img_text_fit(TEXT_EXPIRE,etm,marge,etw,exth)
        img_text_fit(sub,int(wh + marge),marge,wh,exth)
    else:
        print("Error, No valid parameters")
        sys.exit(2)
        
    debug("Saving the file")
    img_save(outFile)        
    debug("Send to printer the result")
    img_print()
    debug("Cleaning")
    img_clean()
    
elif action == "address":
    #-t -t (name) -s (address) -n (city,state,country) -c (postalcode)
    debug("Generate address label")
    print("Error : Action not implented")
    if(text!="" and sub is not False and owner is not False and code is not False):
        th=int(outHeight / 4)-marge
        img_new()
        img_text_fit(text,marge,0,outWidth,th+marge)
        img_text_fit(sub,marge,th+(2 * marge),outWidth,th)
        img_text_fit(owner,marge,(2 * th)+(2 * marge),outWidth,th)
        img_text_fit(code,marge,(3 * th)+(2 * marge),outWidth,th)
    elif(sub is not False and owner is not False and code is not False):
        th=int(outHeight / 3)-marge
        img_new()
        img_text_fit(sub,marge,marge,outWidth,th)
        img_text_fit(owner,marge,th+marge,outWidth,th)
        img_text_fit(code,marge,(2 * th)+marge,outWidth,th)
    else:
        print("Error, No valid parameters")
        sys.exit(2) 
    debug("Saving the file")
    img_save(outFile)        
    debug("Send to printer the result")
    img_print()
    debug("Cleaning")
    img_clean()
    
elif action == "cable":
    #-t -m
    try:
        sidetext=int(((outWidth - cableCenter) / 2) - (2 * marge))
        th=int(img_text_max(text,sidetext,outHeight,"h"))
        tw=int(img_text_max(text,sidetext,outHeight,"w"))
        debug("Generate the workspace")
        img_new(outWidth,int(th + (2 * marge)))
        debug("Adding text to fit the space, at left")
        img_text_fit(text,marge,marge,sidetext,th)
        pl=int(outWidth - (tw + marge)) 
        debug("Adding text to fit the space, at right") 
        img_text_fit(text,pl,marge,tw,th)
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
    
elif action == "archive":
    #-t -c
    debug("Generate archiving label (text with barcode, with display code forced)")
    debug("The barcode is at down of label")
    ts=[marge,0]
    bs=[marge,int((outHeight / 2) - marge)]
    try:
        debug("Generate the workspace")
        img_new()
        debug("Adding text")
        th=img_text_max(text,outWidth,int(outHeight / 2),"h")
        if(owner is not False):
            debug("Adding owner text")
            toh=img_text_max(owner,outWidth,int((outHeight / 6) - marge),"h")
            tow=img_text_max(owner,outWidth,int(toh),"w")
            th=img_text_max(text,outWidth,int((outHeight / 2) - (toh + marge)),"h")
            tm=int((outWidth - tow) / 2)
            debug("Position find is "+str(tow)+"x"+str(toh)+" with marge for centering to "+str(tm))
            img_text_fit(owner,tm,int(marge + th),tow,toh)
        else:
            toh=marge
        debug("Adding text to fit the space") 
        img_text_fit(text,int(ts[0]),int(ts[1]),outWidth,th)
        debug("Generate the barcode")
        img_barcode_gen(str(code),"temp_"+outFile)
        debug("Adding barcode with size for the sub text")
        bh=int(th + toh + (2 * marge))
        img_barcode("temp_"+outFile,str(code),int(outWidth * 0.20),int(bh))
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


