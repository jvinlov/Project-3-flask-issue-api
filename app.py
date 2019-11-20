from flask import Flask, g
from flask_cors import CORS
from resources.issues import issue
import models


DEBUG = True
PORT = 8000


#Initialize an instance of the flask class
#This starts the website!
app = Flask(__name__)

@app.before_request
def before_request():
    """Connect to the database before each request"""
    g.db = models.DATABASE
    g.db.connect()

@app.after_request
def after_request(response):
    """Close the database connection after each request"""
    g.db.close()
    return response



#The default URL ends in  / ('my-website.com')

@app.route('/')
def index():
	return 'hi'


CORS(issue, origins=['http://localhost:3000'], supports_credentials=True)

app.register_blueprint(issue, url_prefix='/api/v1/issues')


#Run the app when the program starts
if __name__ == '__main__':
	models.initialize()
	app.run(debug=DEBUG, port=PORT)
	