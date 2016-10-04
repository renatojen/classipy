"""
* 
* imgrec.py
* Author:
* Renato Jensen Filho
* 2016-10-04
* 
"""

from flask import Flask, render_template, request
from watson_developer_cloud import VisualRecognitionV3 as vr3
import os

#
vr3_key = os.environ.get("WATSON_VR_API_KEY")
if vr3_key == None:      
   print("Environment variable WATSON_VR_API_KEY not set")
   quit()
   
rec = vr3(api_key=vr3_key, version='2016-05-20')
      
application=Flask(__name__)

@application.route('/')
def index():
   return render_template("index.html", label="", img="")

@application.route('/about')
def about():
   return render_template("about.html")
    
# Classify image, save data to database and display image and results
@application.route('/classify', methods=['POST'])
def classify():      
   img_url = None
   if request.method == 'POST':
      img_url = str(request.form['img_url'])
      #Validation of image file
      if img_url.endswith(".jpg") or img_url.endswith(".png"):         
         img_data = rec.classify(images_url=img_url)
         classes = ""
         for data in img_data['images'][0]['classifiers'][0]['classes']:
            classes = classes + '\n'  + str(int(data['score']*100)) + '% chance the image is related to: ' + data['class'] 
            #print('\n' + str(int(data['score']*100)) + '% chance the image is related to: '+ data['class'])            
         
      else:
         return render_template('about.html')
         """
         # Check that email does not already exist (not a great query, but works)
         if not db.session.query(User).filter(User.email == email).count():
         reg = User(email)
         db.session.add(reg)
         db.session.commit()
         return render_template('success.html')    
         """
         
   return render_template('index.html', label=classes, img=img_url)
           
      
if __name__=="__main__":
   application.run(debug=True)