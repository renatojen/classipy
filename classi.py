"""
* 
* classi.py
* Author:
* Renato Jensen Filho
* 2016-10-04
* 
"""

#imports
from flask import Flask, render_template, request
from watson_developer_cloud import VisualRecognitionV3 as vr3, TextToSpeechV1 as ts1
from os import remove, listdir, getenv
from os.path import join, dirname
from datetime import datetime
from time import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from db import Database
from yaml import safe_load, dump

dt = str(datetime.now())[:-5].replace(' ', '_').replace(':', '').replace('.', '') #YYYY-mm-DD_HHMMSSS   
vr = None
ts = None
db = None

#cleans previously generated .ogg files in resources dir
def clean_speech_files():   
   filelist = [ f for f in listdir("./static/resources") if f.endswith(".ogg") and len(f) > 9]
   for f in filelist:
      remove("./static/resources/" + str(f))

#returns a list containing id, img_url and img_classification
def get_images():
   global db
   return db.view()
   
#initialization
def init():
   global vr,ts,db
   cfg = safe_load(open("cfg.yml"))

   #validates VisualRecognitionV3 api key
   vr3_key = getenv("WATSON_VR_API_KEY", cfg['watson']['vr_api_key']) #if WATSON_VR_API_KEY is not set, try local cfg to get api key
   if vr3_key == None or vr3_key == "":
      print("ERROR: Missing api key for Watson's VisualRecognitionV3")
      quit()
   
   #validates TextToSpeechV1 username and password
   ts1_user = getenv("WATSON_TS_USER", cfg['watson']['ts_user'])
   ts1_pswd = getenv("WATSON_TS_PSWD", cfg['watson']['ts_pswd'])
   if ts1_user == None or ts1_user == "" or ts1_pswd == None or ts1_pswd == "":
      print("ERROR: Missing credentials for Watson's TextToSpeechV1")
      quit()
   
   #validates PostgreSQL database URL
   db_url = getenv("CLASSIPY_DB_URL", cfg['db']['url'])
   if db_url == None or db_url == "":   
      print("ERROR: Missing Database URL")
      quit()
      
   #instances a VisualRecognitionV3 object using the api key
   vr = vr3(api_key=vr3_key, version='2016-05-20')

   #instances a TextToSpeechV1 object using the credentials     
   ts = ts1(username=ts1_user, password=ts1_pswd)

   #initializes database
   mrows = cfg['db']['max_rows'] if cfg['db']['max_rows'] != None else 0
   tsize = cfg['db']['tbl_size'] if cfg['db']['tbl_size'] != None else 0
   db = Database(db_url,  mrows,  tsize)

   #creates a scheduler to clean the resources every cfg['app']['clean_speech'] seconds, avoiding running out of disk space
   scheduler = BackgroundScheduler()
   scheduler.start()
   scheduler.add_job(
       func=clean_speech_files,
       trigger=IntervalTrigger(seconds=int(cfg['app']['clean_speech'])),
       id='speech_job',
       name='Speech Cleaner',
       replace_existing=True)
    

init()
    
#
# Flask routines
#

#initializes flask application      
application=Flask(__name__)

@application.route('/')
def index():
   if not "intro.ogg" in listdir("./static/resources/"):
      with open(join(dirname(__file__), "./static/resources/intro.ogg"), 'wb') as audio_file:
         audio_file.write(ts.synthesize("Input an image URL and click the classi pie button!", accept='audio/ogg;codecs=opus', voice="en-US_AllisonVoice"))
         
   return render_template("index.html", label="", img="/static/resources/logo.png", audio_url="intro.ogg", db_data=get_images())
  
#classify image, display image and classification results, generate audio results and save image data to database
@application.route('/', methods=['POST'])
def classify():
   global dt,vr,ts,db
   #updates dt variable (date and time)   
   dt = str(datetime.now())[:-5].replace(' ', '_').replace(':', '').replace('.', '')
   aurl = "output" + dt + ".ogg"      
   prefix = ""
   atxt = ""
   img_url = ""
   if request.method == 'POST':
      img_url = str(request.form['img_url'])
      #Validation of image file
      if img_url.endswith(".jpg") or img_url.endswith(".png"):         
         #calls VisualRecognitionV3 to classify the image
         img_data = vr.classify(images_url=img_url)         
         try:
            for data in img_data['images'][0]['classifiers'][0]['classes']:            
               #prepares the text to speech string            
               atxt = atxt + str(int(data['score']*100)) + '% chance the image is related to: ' + data['class'] + ', '
            #remove the last ', '
            atxt = atxt[:-2]                     
            prefix = "There is "
            #inserts image data on database
            db.insert(img_url, atxt.replace(" chance the image is related to:", ""))
         except KeyError as err:
            atxt = '\n' + "Image not supported. Try classifying another image."
            img_url="/static/resources/logo.png"
            print("ERROR: Invalid dictionary key: " + str(err))                     
      else:
         atxt = '\n' + "Invalid image URL"
         img_url="/static/resources/logo.png"         
       
      #generates audio response (each audio is generated with a different filename (datetime based) to avoid browser cache problems)
      with open(join(dirname(__file__), './static/resources/output' + dt + '.ogg'), 'wb') as audio_file:      
         audio_file.write(ts.synthesize(prefix + atxt.replace('\n', ''), accept='audio/ogg;codecs=opus', voice="en-US_AllisonVoice"))   

   return render_template('index.html', label='\n' + atxt.replace(', ', '\n'), img=img_url, audio_url=aurl, db_data=get_images())           

if __name__=="__main__":
   # Bind to VC_APP PORT/HOST if defined, otherwise default to 5000/localhost.
   PORT = int(getenv('VCAP_APP_PORT', '5000'))
   HOST = str(getenv('VCAP_APP_HOST', 'localhost'))
   application.run(host=HOST, port=PORT)