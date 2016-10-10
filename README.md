# Classipy

Classipy is a python + flask text to speech image recognizer web app. This application uses IBM Watson Visual Recognition service to identify the contents of an image. The results are displayed and spoken to the user, using IBM Watson Text to Speech service. Classipy displays the image and the image results identified by the application. The image data is stored in a PostgreSQL database.

You can see a live version of Classipy here: https://classipy.mybluemix.net/

This live version uses ElephantSQL database as a service to store data.

## Requirements

Runtime:

* python-3.5.1

Python packages:

* APScheduler==3.2.0
* click==6.6
* Flask==0.11.1
* itsdangerous==0.24
* Jinja2==2.8
* MarkupSafe==0.23
* psycopg2==2.6.2
* pysolr==3.5.0
* pytz==2016.7
* PyYAML==3.12
* requests==2.11.1
* six==1.10.0
* tzlocal==1.2.2
* watson-developer-cloud==0.20.0
* Werkzeug==0.11.11

IBM Bluemix services:

* Watson Visual Recognition
* Watson Text to Speech

Database:

* PostgreSQL

##Usage

Input an image url into the text field and click the "Classipy!" button. The page will reload itself, displaying the image, showing and playing the results as speech. The image URL and results are added to the database. The page displays the last n (defined in cfg.yml, 10 by default) records on the database.

## Deploying Classipy on Bluemix

To deploy Classipy on Bluemix you will need:

* Classipy source code
* A Bluemix account
* Cloud Foundry CLI tool
* Watson Visual Recognition and Text to Speech services
* A PostgreSQL database (You can use ElephantSQL for example)

Deploy Steps:

1. Clone Classipy repository
  ```
  $ git clone https://github.com/renatojen/classipy.git
  ```
  This repository contains all necessary files to deploy Classipy on Bluemix, but you need to set the database URL, Watson's Visual Recognition API key and Watson's Text to Speech credentials before running the application. You can choose between setting them as:

  Environment Variables (recommended)  
  You can set them editing manifest.yml or through Bluemix Dashboard:
  * CLASSIPY_DB_URL= the complete url to your PostgreSQL Database 
  * WATSON_TS_PSWD= Watson Text to Speech service password
  * WATSON_TS_USER= Watson Text to Speech service user
  * WATSON_VR_API_KEY= Watson Visual Recognition API key
  
  Configuration File (NOT recommended)  
  Edit cfg.yml:
  * db: url: the complete url to your PostgreSQL Database 
  * watson: ts_pswd: Watson Text to Speech service password
  * watson: ts_user: Watson Text to Speech service user
  * watson: vr_api_key: Watson Visual Recognition API key  

2. Modify cfg.yml and manifest.yml files according to your needs.

3. Connect to Bluemix in the command line tool and follow the prompts to log in.
  ```
  $ cf api https://api.ng.bluemix.net
  $ cf login
  ```

4. Push the app to Bluemix.
  ```
  $ cf push
  ```

## Run the app locally

To run Classipy locally you will need:

* Python 3.5.1 or greater
* Classipy source code
* A Bluemix account
* Watson Visual Recognition and Text to Speech services
* A PostgreSQL database (You can use ElephantSQL for example)

1. Clone Classipy repository
  ```
  $ git clone https://github.com/renatojen/classipy.git
  ```
  This repository contains all necessary files to run Classipy locally, but you need to set the database URL, Watson's Visual Recognition API key and Watson's Text to Speech credentials before running the application. You can choose between setting them as:

  Environment Variables (recommended)    
  * CLASSIPY_DB_URL= the complete url to your PostgreSQL Database 
  * WATSON_TS_PSWD= Watson Text to Speech service password
  * WATSON_TS_USER= Watson Text to Speech service user
  * WATSON_VR_API_KEY= Watson Visual Recognition API key
  
  Configuration File (NOT recommended)  
  Edit cfg.yml:
  * db: url: the complete url to your PostgreSQL Database 
  * watson: ts_pswd: Watson Text to Speech service password
  * watson: ts_user: Watson Text to Speech service user
  * watson: vr_api_key: Watson Visual Recognition API key  

2. Install the required dependencies with pip: in Classipy project folder, run the following command in a command line:
  ```
  $ pip install -r requirements.txt
  ```

3. Modify cfg.yml and manifest.yml files according to your needs.

4. Run the application:
  ```
  $ python classi.py
  ```
  
This command will create a new Flask app and start your application. When your app has started, your console will print the following message:

`Running on http://localhost:5000/ (Press CTRL+C to quit)`.

## Compatibility
Classipy is compatible with the majority of popular browsers such as Google Chrome, Mozilla Firefox, Opera and mobile devices that supports HTML5. There are some known incompatibilities:
  * Audio does not work in Internet Explorer, Safari and some mobile browsers. Internet Explorer does not support .ogg audio files playback (using the audio tag from HTML5).
  * Most mobile browsers does not autoplay the speech. You have to play it manually.

## Troubleshoot

1. Application does not starts after deploy:
   * Check the Bluemix logs
   * Check if the environment variables are set:
   ```
   $ cf env appname
   ```

2. Speech is not being played:
   * Try reloading the page
   * If reloading does not work, try another browser. Check the compatibility section
   
## License
This app is covered by the MIT license. For more information, see LICENSE for license information.
