"""
* 
* imgrec.py
* Author:
* Renato Jensen Filho
* 2016-10-04
* 
"""
#external libraries
from flask import Flask, render_template, request
from watson_developer_cloud import VisualRecognitionV3 as vr3, TextToSpeechV1 as ts1
from os import environ
from os.path import join, dirname

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

#instances a VisualRecognitionV3 object using the api key   
vr = vr3(api_key=vr3_key, version='2016-05-20')

#instances a TextToSpeechV1 object using the credentials  
ts = ts1(username=ts1_user, password=ts1_pswd)

#initializes flask application      
application=Flask(__name__)

@application.route('/')
def index():
   return render_template("index.html", label="", img="", audio="")

@application.route('/about')
def about():
   return render_template("about.html")
    
#classify image, save data to database and display image and results
@application.route('/', methods=['POST'])
def classify():      
   img_url = None
   if request.method == 'POST':
      img_url = str(request.form['img_url'])
      #Validation of image file
      if img_url.endswith(".jpg") or img_url.endswith(".png"):         
         img_data = vr.classify(images_url=img_url)
         atxt = ""
         for data in img_data['images'][0]['classifiers'][0]['classes']:            
            #prepares the text to speech string            
            atxt = atxt + str(int(data['score']*100)) + '% chance the image is related to a'
            if data['class'][0] == 'a' or data['class'][0] == 'e' or data['class'][0] == 'i' or data['class'][0] == 'o' or data['class'][0] == 'u':
               atxt = atxt + 'n '
            else:
               atxt = atxt + ' '
            atxt = atxt + data['class'] + ', '            
         #remove the last ', '
         atxt = atxt[:-2]         
         prefix = "There is a"
         #vowel cases
         if atxt[0] == '8' or atxt.startswith("1%") or atxt.startswith("11") or atxt.startswith("18") or atxt.startswith("100"):
            prefix = prefix + "n "
         else:
            prefix = prefix + " "         
         with open(join(dirname(__file__), './resources/output.wav'), 'wb') as audio_file:
            audio_file.write(ts.synthesize(prefix + atxt, accept='audio/wav', voice="en-US_AllisonVoice"))
      else:
         classes = '\n' + "Invalid image url"
         img_url=""         
         """
         # Check that email does not already exist (not a great query, but works)
         if not db.session.query(User).filter(User.email == email).count():
         reg = User(email)
         db.session.add(reg)
         db.session.commit()
         return render_template('success.html')    
         """
         
   return render_template('index.html', label='\n'+atxt.replace(", ", '\n'), img=img_url, audio="autoplay")
           
      
if __name__=="__main__":
   application.run(debug=True)