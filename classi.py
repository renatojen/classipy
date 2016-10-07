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
from os import environ, remove, listdir, getenv
from os.path import join, dirname
from datetime import datetime
from time import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from db import Database

#cleans previosly generated .ogg files in resources dir
def clean_speech_files():   
   filelist = [ f for f in listdir("./static/resources") if f.endswith(".ogg") and len(f) > 9]
   for f in filelist:
      remove("./static/resources/" + str(f))
      
def get_images():
   global db
   return db.view()
      
#
# Initialization
#

dt = str(datetime.now())[:-5].replace(' ', '_').replace(':', '').replace('.', '') #YYYY-mm-DD_HHMMSSS

#checks for VisualRecognitionV3 api key
vr3_key = environ.get("WATSON_VR_API_KEY")
if vr3_key == None:      
   print("ERROR: Missing api key for Watson's VisualRecognitionV3")
   quit()

#checks for TextToSpeechV1 username and password
ts1_user = environ.get("WATSON_TS_USER")
ts1_pswd = environ.get("WATSON_TS_PSWD")
if ts1_user == None or ts1_pswd == None:      
   print("ERROR: Missing credentials for Watson's TextToSpeechV1")
   quit()

#checks for ElephantSQL database URL
url = environ.get("CLASSIPY_DB_URL")
if url == None:      
   print("ERROR: Missing Database URL")
   quit()

#instances a VisualRecognitionV3 object using the api key      
vr = vr3(api_key=vr3_key, version='2016-05-20')

#instances a TextToSpeechV1 object using the credentials     
ts = ts1(username=ts1_user, password=ts1_pswd)

#instances database
db = Database(url)

#creates a scheduler to clean the resources every 30s, avoiding server overload
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=clean_speech_files,
    trigger=IntervalTrigger(seconds=30),
    id='speech_job',
    name='Speech cleaner',
    replace_existing=True)
    
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
         
   return render_template("index.html", label="", img="", audio_url="intro.ogg", db_data=get_images())

@application.route('/about')
def about():
   return render_template("about.html")
   
#classify image, display image and classification results, generate results audio and save image data to database
@application.route('/', methods=['POST'])
def classify():
   global dt ,vr,ts,db
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
         img_data = vr.classify(images_url=img_url)         
         try:
            for data in img_data['images'][0]['classifiers'][0]['classes']:            
               #prepares the text to speech string            
               atxt = atxt + str(int(data['score']*100)) + '% chance the image is related to: ' + data['class'] + ', '
            #remove the last ', '
            atxt = atxt[:-2]                     
            prefix = "There is "
            db.insert(img_url, atxt.replace(" chance the image is related to:", ""))
         except KeyError as err:
            atxt = '\n' + "Image not supported. Try classifying another image."
            img_url=""
            print("ERROR: Invalid dictonary key: " + str(err))                     
      else:
         atxt = '\n' + "Invalid image URL"
         img_url=""         
       
      #generates audio response (each audio is generated with a different filename (datetime based) to avoid browser cache problems)
      with open(join(dirname(__file__), './static/resources/output' + dt + '.ogg'), 'wb') as audio_file:      
         audio_file.write(ts.synthesize(prefix + atxt.replace('\n', ''), accept='audio/ogg;codecs=opus', voice="en-US_AllisonVoice"))   

   return render_template('index.html', label='\n' + atxt.replace(', ', '\n'), img=img_url, audio_url=aurl, db_data=get_images())           

if __name__=="__main__":
   # Bind to PORT/HOST if defined, otherwise default to 5050/localhost.
   PORT = int(getenv('VCAP_APP_PORT', '5000'))
   HOST = str(getenv('VCAP_APP_HOST', 'localhost'))
   application.run(host=HOST, port=PORT)
   #application.run(debug=True)