from os import path, urandom
import os
import certifi
from dotenv import load_dotenv
import random
from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from datetime import date, datetime, timedelta, timezone
import datetime as dt
from authlib.integrations.flask_client import OAuth
import uuid
import subprocess

import google.generativeai as genai
from google.auth import load_credentials_from_file
from google.oauth2 import credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.generativeai import generative_models
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar',  'https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/documents']


app = Flask(__name__)
app.secret_key = urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")
client = MongoClient(MONGODB_URL, tlsCAFile=certifi.where())

oauth = OAuth(app)
oauth.register(
    "oauthApp",
    client_id='GSlRU8ssqQmC7BteFwhCLqxonlmtvSBP',
    client_secret='4YFxFjzvuXtXyYMoJ9coyCHDphXdUYMAGNF3gcwpZh16Hv-Hz_s83TqawI0RmR2b',
    api_base_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com',
    access_token_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com/oauth/token',
    authorize_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com/oauth/authorize',
    client_kwargs={'scope': 'scope_required_by_provider'}
)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    

@app.route("/")
def mainpage():
    return render_template("main.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    auth_params = {"screen_hint": "signup"}
    return oauth.create_client("oauthApp").authorize_redirect(redirect_uri=url_for('authorized', _external=True), **auth_params)

@app.route("/login", methods=["GET", "POST"])
def login():
    return oauth.create_client("oauthApp").authorize_redirect(redirect_uri=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    # Clear token.json and credentials.json if they exist
    if os.path.exists('token.json'):
        os.remove('token.json')
    
    # Redirect to the main page or any desired page after logout
    return redirect(url_for('mainpage'))

def get_auth0_client_info():
    # Make a GET request to the Auth0 API endpoint
    response = requests.get(AUTH0_API_ENDPOINT)

    # Check if the request was successful
    if response.status_code == 200:
        auth0_info = response.json()
        return auth0_info
    else:
        # Handle the case when the request fails
        raise Exception(f"Failed to retrieve Auth0 client info: {response.status_code} - {response.text}")

@app.route('/authorized')
def authorized():
    token = oauth.oauthApp.authorize_access_token()
    oauth_token = token['access_token']
    session['oauth_token'] = oauth_token

    # Check if credentials.json exists, if not, create it
    if not path.exists("credentials.json"):
        # Construct credentials dictionary
        credentials = {
            "client_id": re,
            "client_secret": 'YOUR_CLIENT_SECRET',
            "auth_uri": 'YOUR_AUTH_URI',
            "token_uri": 'YOUR_TOKEN_URI',
            "auth_provider_x509_cert_url": 'YOUR_AUTH_PROVIDER_CERT_URL'
        }

        # Write credentials to credentials.json
        with open('credentials.json', 'w') as file:
            json.dump(credentials, file)
            
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                if os.path.exists("token.json"):
                    os.remove("token.json")
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port = 0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())
    
    global user_logged_in
    user_logged_in = True
    return redirect(url_for('chatbot'))

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    model = genai.GenerativeModel('models/gemini-pro')
    if 'chat_history' not in session:
        session['chat_history'] = []

    chat_history = session['chat_history']

    response = None
    formatted_message = ""

    if request.method == 'POST':
        user_message = request.form.get('message')
        chat_history.append({'role': 'user', 'parts': [user_message]})
        response = model.generate_content(chat_history)
        chat_history.append({'role': 'model', 'parts': [response.text]})
        session['chat_history'] = chat_history
        if response:
            lines = response.text.split("\n")
            for line in lines:
                bold_text = ""
                while "**" in line:
                    start_index = line.index("**")
                    end_index = line.index("**", start_index + 2)
                    bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
                    line = line[:start_index] + bold_text + line[end_index + 2:]
                formatted_message += line + "<br>"
            # print(formatted_message)

    return render_template("chatbot.html", response=formatted_message)

@app.route("/send-message", methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data.get('message')

    chat_history = data.get('chat_history', [])

    chat_history.append({'role': 'user', 'parts': [user_message]})

    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content(chat_history)
    bot_response = response.text
    formatted_message = ""
    lines = bot_response.split("\n")
    for line in lines:
        bold_text = ""
        while "**" in line:
            start_index = line.index("**")
            end_index = line.index("**", start_index + 2)
            bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
            line = line[:start_index] + bold_text + line[end_index + 2:]
        formatted_message += line + "<br>"
    # print(formatted_message)
    
    return jsonify({'message': formatted_message, 'chat_history': chat_history})



if __name__ == "__main__":
    app.run(debug=True)