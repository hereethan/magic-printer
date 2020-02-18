## Import necessary libraries
from flask import Flask, render_template, request
from weasyprint import HTML, CSS
from flask_mail import Mail, Message
import os
import logging
import datetime
import requests
from darksky import forecast
import datetime
from datetime import date, timedelta
import random
import string
from flask_basicauth import BasicAuth

app = Flask(__name__, static_url_path = "", static_folder = "")

## Make sure you update and insert in your server's accurate variables throughout
## the app
## Variable values that you need to customize include:
## (YOUR-USERNAME, YOUR-PASSWORD, SMTP-SERVER-DOMAIN, PORT-NUMBER, INSERT-USERNAME,
## INSERT-PASSWORD, INSERT-SUBJECT-NAME, MAIL_USERNAME, RECIPIENTS-E-MAIL-ADDRESS,
## API-ACCESS-KEY, TYPE IN BODY FOR E-MAIL)

## Very basic authentication settings - update username and password
app.config['BASIC_AUTH_USERNAME'] = 'YOUR-USERNAME'
app.config['BASIC_AUTH_PASSWORD'] = 'YOUR-PASSWORD'
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app) ## Set authentication for entire website.

## Set up logging for HTML to PDF conversation process
logger = logging.getLogger('weasyprint')
logger.addHandler(logging.FileHandler('/tmp/weasyprint.log'))

## Set up your SMTP mail settings
mail_settings = {
    "MAIL_SERVER": 'SMTP-SERVER-DOMAIN',
    "MAIL_PORT": PORT-NUMBER,
    ## Insert either False or True in the below security settings(no quotes)
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'INSERT-USERNAME',
    "MAIL_PASSWORD": 'INSERT-PASSWORD'
}
app.config.update(mail_settings)
mail = Mail(app)

## Pass along date and time to postoffice website
@app.context_processor
def inject_now():
    return {'now': datetime.date.today()}

## Homepage for postoffice
@app.route('/')
@basic_auth.required
def postbox():
       return render_template('index.html')

## Convert typed message into a PDF, mail it, and then forward to 'success' page
@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
          ## Create dict to hold message content
          content = {}
          ## Create key and values in content dict from what was typed into form
          for key,value in request.form.items():
              content[key]=value
          ## Pass along dict to message page for PDF creation.
          html = render_template("result.html",result = content)
          ## Create random name generator for resulting PDF
          rand_str = lambda n: ''.join([random.choice(string.ascii_lowercase) for i in range(n)])
          ## Create variable that will hold random name of resulting PDF
          file_attachment = rand_str(10)+".pdf"

          ## Write submitted content into PDF with generated name
          with open(file_attachment,"w") as f:
              HTML(string=html,base_url=__file__).write_pdf(file_attachment)

          ## Mail PDF to specified e-mail & customize subject and who gets the e-mail
          with app.app_context():
              msg = Message(subject="INSERT-SUBJECT-NAME",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=["RECIPIENTS-E-MAIL-ADDRESS"],
                      body="TYPE IN BODY FOR E-MAIL")
          ## Attach PDF in e-mail
              with app.open_resource(file_attachment) as fp:
                  msg.attach(file_attachment,"image/pdf",fp.read())
                  mail.send(msg)

          ## After sending PDF, delete the file in server directory
              if os.path.exists(file_attachment):
                   os.remove(file_attachment)
          return render_template('sent.html')

## Weather app using DarkSky API
@app.route('/weather')
def weather():
       ## Set weather coordinates & rename variable if you like!
       BOSTON = 40.601140, -75.600590
       weekday = date.today()
       ## Insert in API key below
       with forecast('API-ACCESS-KEY', *BOSTON) as boston:
           today = boston.daily[0]
           ## Insert weather forcast into variable 'day'
           day = dict(day = date.strftime(weekday, '%a'),
                              sum = today.summary,
                              tempMin = today.temperatureMin,
                              tempMax = today.temperatureMax,
                              icon = today.icon,
                              )
           ## Create variable to store string text to be included on 'weather' page
           weather = str('{sum} Lows of {tempMin} and highs of {tempMax}'.format(**day))
           ## Create variable that is named to the approriate icon
           weather_icon_API = day['icon']
           ## Create dictionary to connect each potential forecast's icon to corresponding file
           icon_database = {
            'clear-day':'images/clear.jpg',
            'clear-night':'images/clear-night.jpg',
            'rain':'images/rain.jpg',
            'snow':'images/snow.jpg',
            'sleet':'images/sleet.jpg',
            'wind':'images/wind.jpg',
            'fog':'images/fog.jpg',
            'cloudy': 'images/cloudy.jpg',
            'partly-cloudy-day':'images/partly-cloudy.jpg',
            'partly-cloudy-night':'images/partly-cloudy-night.jpg',
            'hail':'images/hail.jpg',
            'thunderstorms':'images/thudnerstorm.jpg',
            'tornado':'images/tornado.jpg'
           }
           ## Create variable that points to the correct weather icon
           weather_icon = icon_database[weather_icon_API]

           ## Time to include bad jokes into the weather page via a public API
           url = 'https://icanhazdadjoke.com/'
           headers = {'Accept': 'application/json'}
           ## Store bad joke into variable
           joke_msg = requests.get(url, headers=headers).json().get('joke')
           ## Print bad joke for debugging purposes (and in case you'd like a laugh...)
           print(joke_msg)

           ## Send necessary variables back to flask to then be included into website and resulting file
           ## Including: weather = forecast, weather_icon = forecast icon, joke_msg = bad joke
           html = render_template('weather.html',weather=weather,weather_icon=weather_icon,joke_msg=joke_msg)
           ## Create random name generator for resulting PDF
           rand_str = lambda n: ''.join([random.choice(string.ascii_lowercase) for i in range(n)])
           ## Create variable that will hold random name of resulting PDF
           file_attachment = rand_str(10)+".pdf"

           ## Write submitted content into PDF with generated name
           with open(file_attachment,"w") as f:
               HTML(string=html,base_url=__file__).write_pdf(file_attachment)

          ## Mail PDF to specified e-mail & customize subject and who gets the e-mail
          with app.app_context():
              msg = Message(subject="INSERT-SUBJECT-NAME",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=["RECIPIENTS-E-MAIL-ADDRESS"],
                      body="TYPE IN BODY FOR E-MAIL")
           ## Attach PDF
              with app.open_resource(file_attachment) as fp:
                  msg.attach(file_attachment,"image/pdf",fp.read())
                  mail.send(msg)
           ## Delte PDF from server after sent
              if os.path.exists(file_attachment):
                   os.remove(file_attachment)
                   ## return required variables so that they can be rendered in Flask app
                   return render_template('weather.html',weather=weather,weather_icon=weather_icon,joke_msg=joke_msg)

## App to generate a random turtle fact from a list
@app.route('/turtle')
def turtle():
           ## Open & read the file that includes all the turtle facts!
           infile = open('turtles.txt', 'r')
           turtleFact = infile.readline()
           print (turtleFact)
           with open('turtles.txt', 'r') as turtle:
               data = turtle.read().splitlines(True)
           ## Delete the fact after it is stored in the variable
           with open('turtles.txt', 'w') as fout:
               fout.writelines(data[1:])
           ## Send the necessary variable back to flask
           html = render_template('turtle.html',turtleFact=turtleFact)

           ## Create random name generator for resulting PDF
           rand_str = lambda n: ''.join([random.choice(string.ascii_lowercase) for i in range(n)])
           ## Attach PDF
           file_attachment = rand_str(10)+".pdf"
           with open(file_attachment,"w") as f:
               HTML(string=html,base_url=__file__).write_pdf(file_attachment)

          ## Mail PDF to specified e-mail & customize subject and who gets the e-mail
          with app.app_context():
              msg = Message(subject="INSERT-SUBJECT-NAME",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=["RECIPIENTS-E-MAIL-ADDRESS"],
                      body="TYPE IN BODY FOR E-MAIL")
              with app.open_resource(file_attachment) as fp:
                  msg.attach(file_attachment,"image/pdf",fp.read())
                  mail.send(msg)
              if os.path.exists(file_attachment):
                   os.remove(file_attachment)
                   return render_template('turtle.html',turtleFact=turtleFact)

def weather_request():
    response = requests.get("http://127.0.0.1:5000/weather")


if __name__ == '__main__':
   app.run(debug = True)

##      for item in result.items():
##		key = item.keys[0]
##      value = item[key]
