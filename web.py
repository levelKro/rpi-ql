#!/usr/bin/python3
import urllib.parse as urlparse
import http.server
import socketserver
import os
import subprocess
import configparser
import json
import datetime
import time
from threading import Timer
from urllib.parse import parse_qs
from os import path
from datetime import datetime as dt
from os import listdir
from os.path import isfile, join, isdir
from subprocess import Popen

print("Starting Web Server script")
scriptpath=os.path.dirname(os.path.realpath(__file__))+"/"
print(" * Loading configuration file: "+scriptpath+"config.ini")
config = configparser.ConfigParser()
config.read(scriptpath+"config.ini", encoding='utf-8')
print("Setting web directory")
WEBPATH=scriptpath + config["web"]["path"]
#os.chdir(WEBPATH)



class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    update = False
    def do_GET(self):
        if self.path == '/':
            self.path = "/index.html"
        pathSplit = self.path.split("?")
        try:
            self.runPage(pathSplit[0],pathSplit[1])
        except:
            self.runPage(pathSplit[0])
            pass
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        postDatas = post_data.decode("utf-8")
        if self.path == '/':
            self.path = "/index.html"
        pathSplit = self.path.split("?")
        try:
            self.runPage(pathSplit[0],pathSplit[1],postDatas)
        except:
            self.runPage(pathSplit[0],"",postDatas)
            pass

    def runPage(self,page,getDatas="",postDatas=""):
        pathSection = page.split("/")
        print("** URL: "+page)
        print("** _GET: "+getDatas)
        print("** _POST: "+postDatas)
        
        try:
            getDatas = urlparse.parse_qs(getDatas.replace('"',"''"))
        except:
            getDatas=""
            pass
        try:
            postDatas = urlparse.parse_qs(postDatas.replace('"',"''"))
        except:
            postDatas=""
            pass
        
        if path.exists(WEBPATH+page) is True:
            self.path = page
            try:
                f = open(WEBPATH+self.path, 'rb')
            except OSError:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes('Document requested is not found.', "utf-8"))
                return None

            ctype = self.guess_type(self.path)
            fs = os.fstat(f.fileno())

            self.send_response(200)
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified",
                self.date_time_string(fs.st_mtime))
            self.end_headers()            

            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()
            ##return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        elif pathSection[1] == "print":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            outputJson={"result":"error","reason":"Invalid action"}
            values=""
            try:
                if(int(postDatas['copie'])<=0):
                    copie=1
                else:
                    copie=int(postDatas['copie'])
            except:
                copie=1
               
            try:
                if pathSection[2] == "text":
                    if(postDatas.get('text') is not None):
                        values=values+' -a text -k "'+str(copie)+'" -t "'+str(postDatas['text'])+'"'
                        outputJson={"result":"success","reason":"Printing text label."}
                        self.goPrint(str(values))
                    else:
                        outputJson={"result":"error","reason":"Text is missing."}
                        
                elif pathSection[2] == "textLarge":
                    if(postDatas.get('text') is not None):
                        values=values+' -a textlarge -k "'+str(copie)+'" -t "'+str(postDatas['text'])+'"'
                        outputJson={"result":"success","reason":"Printing large text label."}
                        self.goPrint(str(values))
                    else:
                        outputJson={"result":"error","reason":"Text is missing."}
                        
                elif pathSection[2] == "textImage":
                    if(postDatas.get('text') is not None):
                        values=values+' -a textimage -k "'+str(copie)+'" -t "'+str(postDatas['text'])+'"'
                        if(postDatas.get('image') is not None):
                            #if exists
                            values=values+' -i "'+postDatas['image']+'"'
                        else:
                            if(postDatas.get('x') is not None):
                                values=values+' -x "'+postDatas['x']+'"'
                            if(postDatas.get('y') is not None):
                                values=values+' -y "'+postDatas['y']+'"'
                            if(postDatas.get('position') is not None!=""):
                                values=values+' -d "'+postDatas['position']+'"'
                            if(postDatas.get('mode') is not None!=""):
                                values=values+' -r "'+postDatas['mode']+'"'
                            outputJson={"result":"success","reason":"Printing text with image label."}
                            self.goPrint(str(values))
                    else:
                        outputJson={"result":"error","reason":"Text is missing."}
                        
                elif pathSection[2] == "cable":
                    if(postDatas.get('text') is not None):
                        values=values+' -a cable -k "'+str(copie)+'" -t "'+str(postDatas['text'])+'"'
                        outputJson={"result":"success","reason":"Printing cable text label."}
                        self.goPrint(str(values))
                    else:
                        outputJson={"result":"error","reason":"Text is missing."}
                        
                elif pathSection[2] == "barcode":
                    if(postDatas.get('text') is not None):
                        values=values+' -a barcode -k "'+str(copie)+'" -t "'+str(postDatas['text'])+'"'
                        if(postDatas.get('code') is not None):
                            values=values+' -c "'+str(postDatas['code'])+'"'
                            if(postDatas.get('position') is not None!=""):
                                values=values+' -d "'+str(postDatas['position'])+'"'
                            if(postDatas.get('sub') is not None!=""):
                                values=values+' -s "'+str(postDatas['sub'])+'"'
                            outputJson={"result":"success","reason":"Printing barcode label."}
                            self.goPrint(str(values))
                        else:
                            outputJson={"result":"error","reason":"String to encode is missing."}
                            
                elif pathSection[2] == "archive":
                    if(postDatas.get('text') is not None):
                        values=values+' -a archive -k "'+str(copie)+'" -t "'+str(postDatas['text'])+'"'
                        if(postDatas.get('code') is not None):
                            values=values+' -c "'+str(postDatas['code'])+'"'
                            if(postDatas.get('sub') is not None):
                                values=values+' -n "'+str(postDatas['sub'])+'"'
                            outputJson={"result":"success","reason":"Printing archive label."}
                            self.goPrint(str(values))
                        else:
                            outputJson={"result":"error","reason":"String to encode is missing."}
                    
                elif pathSection[2] == "expire":
                    if(postDatas.get('packed') is not None or postDatas.get('expired') is not None ):
                        values=values+' -a expire -k "'+str(copie)+'"'
                        if(postDatas.get('text') is not None):
                            values=values+' -t "'+str(postDatas['text'])+'"'
                        if(postDatas.get('packed') is not None):
                            values=values+' -n "'+str(postDatas['packed'])+'"'
                        if(postDatas.get('expired') is not None):
                            values=values+' -s "'+str(postDatas['expired'])+'"'
                        outputJson={"result":"success","reason":"Printing expiration label."}
                        self.goPrint(str(values))
                    else:    
                        outputJson={"result":"error","reason":"No date to show."}
                    
                elif pathSection[2] == "address":
                    if(postDatas.get('civic') is not None and postDatas.get('region') is not None and postDatas.get('postal') is not None ):
                        values=values+' -a address -k "'+str(copie)+'"'
                        if(postDatas.get('text') is not None):
                            values=values+' -t "'+str(postDatas['text'])+'"'
                        values=values+' -n "'+str(postDatas['civic'])+'" -s "'+str(postDatas['region'])+'" -c "'+str(postDatas['postal'])+'"'
                        outputJson={"result":"success","reason":"Printing expiration label."}
                        self.goPrint(str(values))
                    else:    
                        outputJson={"result":"error","reason":"Require the civic address, region and postal code."}
                        
                elif pathSection[2] == "cli":
                    print("CLI")
                    if(postDatas.get('parameters') is not None):
                        params=str(postDatas['parameters']).replace('["',"").replace('"]',"").replace("''",'"')
                        outputJson={"result":"success","reason":"Send to cli script the parameter; "+params+"."}
                        self.goPrint(" "+params)
                    else:
                        print("NO PARAMS")
            except:
                outputJson={"result":"error","reason":"Error when processing the request."}
                pass
                    
            return self.wfile.write(bytes(json.dumps(outputJson), "utf-8"))
        
        elif pathSection[1] == "manage":
            print(" * Loading configuration file: "+scriptpath+"config.ini")
            config = configparser.ConfigParser()
            config.read(scriptpath+"config.ini", encoding='utf-8')
            outputJson={"result":"error","reason":"Invalid action"}
            if(postDatas.get('password') is not None):
                if(str(postDatas.get('password')).replace("['","").replace("']","")==str(config['web']['adminpass'])):
                    try:
                        if pathSection[2] == "reboot":
                            outputJson={"result":"success","reason":"Rebooting system..."}
                            tmp=subprocess.Popen(['./cli-reboot.sh'])
                        elif pathSection[2] == "poweroff":
                            outputJson={"result":"success","reason":"Poweroff system..."}
                            tmp=subprocess.Popen(['./cli-poweroff.sh'])
                        elif pathSection[2] == "update":
                            if(len(pathSection)==4):
                                try:
                                    if(pathSection[3]=="log"):
                                        page="../update.log"
                                        if path.exists(WEBPATH+page) is True:
                                            self.path = page
                                            try:
                                                f = open(WEBPATH+self.path, 'rb')
                                            except OSError:
                                                self.send_response(404)
                                                self.send_header("Content-type", "text/html")
                                                self.end_headers()
                                                self.wfile.write(bytes("Can't open log file.", "utf-8"))
                                                return None

                                            ctype = self.guess_type(self.path)
                                            fs = os.fstat(f.fileno())

                                            self.send_response(200)
                                            self.send_header("Content-type", ctype)
                                            self.send_header("Content-Length", str(fs[6]))
                                            self.send_header("Last-Modified",
                                                self.date_time_string(fs.st_mtime))
                                            self.end_headers()            

                                            try:
                                                self.copyfile(f, self.wfile)
                                            finally:
                                                f.close()
                                            ##return http.server.SimpleHTTPRequestHandler.do_GET(self)
                                            return 
                                        else:
                                            self.send_response(404)
                                            self.send_header("Content-type", "text/html")
                                            self.end_headers()
                                            self.wfile.write(bytes('No update running.', "utf-8"))
                                            return None                         
                                except:
                                    outputJson={"result":"error","reason":"Error when processing the request."}
                            else:
                                outputJson={"result":"success","reason":"Updating system..."}
                                run=False
                                try:
                                    if(self.update is not False):
                                        if(self.update.returncode is None):
                                            run=True
                                except:
                                    pass
                                if(run is False):
                                    self.update = subprocess.Popen(['./cli-update.sh'])
                        elif pathSection[2] == "config":
                            if pathSection[3] == "load":
                                result="{"
                                readconfig = configparser.ConfigParser()
                                readconfig.read('config.ini', encoding='utf-8')
                                for s in readconfig.sections():
                                    result=result+'"'+str(s)+'":{'
                                    for o,v in readconfig.items(s):
                                        if(str(o)!="adminpass"):
                                            result=result+'"'+str(o)+'":"'+str(v)+'",'
                                    result=result+'},'
                                    
                                result=result+"}"
                                result=result.replace(",}","}")

                                outputJson={"result":"success","reason":"Reading configuration.","datas":json.loads(result)}
                                
                            elif pathSection[3] == "save":
                                saveconfig = configparser.ConfigParser()
                                saveconfig.read('config.ini', encoding='utf-8')
                                
                                if(postDatas.get('model') is not None):
                                    saveconfig['printer']['model']=str(postDatas['model']).replace("['","").replace("']","")
                                if(postDatas.get('usb') is not None):
                                    saveconfig['printer']['usb']=str(postDatas['usb']).replace("['","").replace("']","")
                                if(postDatas.get('serial') is not None):
                                    saveconfig['printer']['serial']=str(postDatas['serial']).replace("['","").replace("']","")
                                    
                                with open('config.ini', 'w', encoding='utf-8') as configfile:    # save
                                    saveconfig.write(configfile)
                                
                                result="{"
                                saveconfig = configparser.ConfigParser()
                                saveconfig.read('config.ini', encoding='utf-8')
                                for s in saveconfig.sections():
                                    result=result+'"'+str(s)+'":{'
                                    for o,v in saveconfig.items(s):
                                        if(str(o)!="adminpass"):
                                            result=result+'"'+str(o)+'":"'+str(v)+'",'
                                    result=result+'},'
                                    
                                result=result+"}"
                                result=result.replace(",}","}")

                                outputJson={"result":"success","reason":"Saving configuration.","datas":json.loads(result)}                                    
                            else:
                                print("Error in config")
                                outputJson={"result":"error","reason":"This action is not valid."}
                        else:
                           outputJson={"result":"error","reason":"Request is not valid."} 
                    except Exception as e:
                        print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
                        outputJson={"result":"error","reason":"Error when processing the request."}
                        pass
                else:    
                    outputJson={"result":"error","reason":"Password is incorrect."}
            else:
                outputJson={"result":"error","reason":"No password or not in POST method."}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()                
            return self.wfile.write(bytes(json.dumps(outputJson), "utf-8"))
        
        elif pathSection[1] == "version":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            outputJson={"result":"success","web":"2.2.1106","rpiql":"1.2.1106","rpiqlgui":"1.2.1106"}
            return self.wfile.write(bytes(json.dumps(outputJson), "utf-8"))
        
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes('Document requested is not found.', "utf-8"))
        return
        
    def goPrint(self,values):
        print("Send to printer : "+str(values))
        try:
            os.system('python3 core.py'+str(values).replace("['","").replace("']",""))
        except:
            ##tmp=subprocess.Popen('python3 core.py'+str(values).replace("['","").replace("']",""), shell=True)
            print("Can't run the command.")
            
def start():
    pcStats = MyHttpRequestHandler
    pcStatsServer = socketserver.TCPServer(("0.0.0.0", int(config['web']['port'])), pcStats)
    print("*** RUNNING WEB SERVER AT PORT "+str(config['web']['port'])+" ***")
    pcStatsServer.serve_forever()

            
start()            
            