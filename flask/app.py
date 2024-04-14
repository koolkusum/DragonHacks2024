import json
from os import path, urandom
import os
import certifi
from dotenv import load_dotenv
import random
from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g, session
import mongoengine
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import send_from_directory
from werkzeug.utils import secure_filename
from mongoengine import Document, StringField, ListField, BooleanField, IntField


from datetime import date, datetime, timedelta, timezone
import datetime as dt
from authlib.integrations.flask_client import OAuth
import uuid
import subprocess
import PyPDF2

import google.generativeai as genai
from google.auth import load_credentials_from_file
from google.oauth2 import credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.generativeai import generative_models
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

from calendarinter import convert_to_iso8601, delete_calendar_event, get_credentials, parse_datetime_to_day_number, parse_event_details

admin_mode = True

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

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

mongoengine.connect(host=MONGODB_URL, tlsCAFile=certifi.where())
class Course(Document):
    cid = IntField(required=True, unique=True)
    name = StringField(required=True)
    pids = ListField(IntField())
    lesson = StringField()
    coding = BooleanField()
    theory = BooleanField()
    meta = {
        'collection': 'courses'
    }
    
    def add_pid(self, pid):
        if pid not in self.pids:
            self.pids.append(pid)
            # pass through set
            self.pids = list(set(self.pids))
            self.save()

    def delete_pid(self, pid):
        if pid in self.pids:
            self.pids.remove(pid)
            self.save()
            
    def set_lesson(self, lesson):
        self.lesson = lesson
        self.save()

class Professor(Document):
    pid = IntField(required=True, unique=True)
    name = StringField(required=True, unique=True)
    desc = StringField(required=True)
    rating = IntField()
    rids = ListField(IntField())
    attendance = BooleanField()
    cids = ListField(IntField())
    meta = {
        'collection': 'professors'
    }

    last_pid = None  # Static variable to store the last PID

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the pid automatically if not provided
        if not self.pid:
            if Professor.last_pid is None:
                last_professor = Professor.objects.order_by('-pid').first()
                Professor.last_pid = last_professor.pid if last_professor else 0
            Professor.last_pid += 1
            self.pid = Professor.last_pid
            
    def create_review(self, title, description, cid):
        review = Review(
            rid = 1,
            title=title,
            desciption=description,
            cid=cid,
            pid=self.pid
        )
        review.save()
        self.rids.append(review.rid)
        self.save()
    
    def add_cid(self, cid):
        # Check if the CID is already in the list
        if cid not in self.cids:
            self.cids.append(cid)
            # pass through set to make sure uniqueness
            self.cids = list(set(self.cids))
            self.save()
            print(f'CID {cid} added to Professor {self.name}')
        else:
            print(f'CID {cid} already exists in Professor {self.name}')
            
    def delete_cid(self, cid):
        # Check if the CID is in the list
        if cid in self.cids:
            self.cids.remove(cid)
            self.save()
            print(f'CID {cid} deleted from Professor {self.name}')
        else:
            print(f'CID {cid} not found in Professor {self.name}')

class Review(Document):
    rid = IntField(required=True, unique=True)
    pid = IntField(required=True)
    title = StringField(required=True)
    desciption = StringField(required=True)
    cid=IntField(required=True)
    meta = {
        'collection': 'reviews'
    }
    
    def __init__(self, *args, **kwargs):
        super(Review, self).__init__(*args, **kwargs)
        if not self.rid:
            last_review = Review.objects.order_by('-rid').first()
            if last_review:
                self.rid = last_review.rid + 1
            else:
                self.rid = 1
    

def load():
    return
#     course1=Course(
#     cid=111,
#     pids=[0],
#     name = "Introduction to Computer Science",
#     lesson = "Teach the princples of Java programming.",
#     coding = True,
#     theory = False
# )
#     course1.save()
    
    # prof1= Professor(
    # pid = 0,
    # name = "Ana Centeno",
    # desc="Ana Centeno is head coordinator of Introduction to Computer Science and  Data Structures.",
    # attendance = False,
    # cids = [111]
    # )
    # prof1.save()
    
    # prof2 = Professor(
    # pid = 1,
    # name = "Brian Harrington",
    # desc="Brian Harrington is a professor of Data Structures and Algorithms.",
    # attendance = False,
    # cids = [111]
    # )
    # prof2.save()
    # print("prof2 saved")
    
    # review1 = Review(
    # rid = 0,
    # pid = 0,
    # title = "Centeno is the best professor",
    # desciption ="She is super understanding and caring of her students and does her best to make sure they pass.",
    # cid=111
    # )
    # review1.save()
     
@app.route("/")
def mainpage():
    # load()
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

# @app.route('/authorized')
# def authorized():
#     token = oauth.oauthApp.authorize_access_token()
#     oauth_token = token['access_token']
#     session['oauth_token'] = oauth_token

#     # Check if credentials.json exists, if not, create it
#     if not path.exists("credentials.json"):
#         # Construct credentials dictionary
#         credentials = {
#             "client_id": re,
#             "client_secret": 'YOUR_CLIENT_SECRET',
#             "auth_uri": 'YOUR_AUTH_URI',
#             "token_uri": 'YOUR_TOKEN_URI',
#             "auth_provider_x509_cert_url": 'YOUR_AUTH_PROVIDER_CERT_URL'
#         }

#         # Write credentials to credentials.json
#         with open('credentials.json', 'w') as file:
#             json.dump(credentials, file)
            
#     creds = None
#     if os.path.exists("token.json"):
#         creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             try:
#                 creds.refresh(Request())
#             except Exception as e:
#                 if os.path.exists("token.json"):
#                     os.remove("token.json")
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
#             creds = flow.run_local_server(port = 0)

#             with open("token.json", "w") as token:
#                 token.write(creds.to_json())
    
#     global user_logged_in
#     user_logged_in = True
#     return redirect(url_for('chatbot'))
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


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "pdf_file" not in request.files:
            return "No file part"

    

        pdf_file = request.files["pdf_file"]

        if pdf_file.filename == "":
            return "No selected file"

        if pdf_file:
            pdf_text = extract_text_from_pdf(pdf_file)
            query = "As a chatbot, your goal is to summarize the following text from a PDF in a format that is easily digestible for a college student. Try to keep it as concise as possible can: " + pdf_text
            model = genai.GenerativeModel('models/gemini-pro')
            result = model.generate_content(query)
            formatted_message = ""
            lines = result.text.split("\n")
            # print(result.text)
            for line in lines:
                bold_text = ""
                while "**" in line:
                    start_index = line.index("**")
                    end_index = line.index("**", start_index + 2)
                    bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
                    line = line[:start_index] + bold_text + line[end_index + 2:]
                formatted_message += line + "<br>"
            filename = secure_filename(pdf_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            filepath = filepath.replace('\\','/')
            print(filepath)
            def copy_file(source_path, destination_path):
                try:
                    subprocess.run(['copy', source_path, destination_path], shell=True)
                    print(f"File copied from {source_path} to {destination_path} successfully.")
                except Exception as e:
                    print(f"Error occurred: {str(e)}")

            # Example usage:
            source_path = os.path.abspath(f'./static/{filename}')
            destination_path = os.path.abspath(f'./static/{filepath}')

            copy_file(source_path, destination_path)
            print(filename)
            session['current_filename'] = filename
            session['current_pdf'] = True
            
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

            service = build("docs", "v1", credentials=creds)
            doc = {
                'title': filename + " - Summarized"
            }
            doc = service.documents().create(body=doc).execute()
            doc_id = doc.get('documentId')

            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': result.text,
                    }
                }
            ]
            result = service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

            doc_url = f"https://docs.google.com/document/d/{doc_id}"

            return render_template("upload.html", formatted_message=formatted_message, current_pdf=True, filename=filename)

    return render_template("upload.html")


@app.route("/show_pdf")
def show_pdf():
    if 'current_filename' in session:
        filename = session['current_filename']
        print(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print (filepath)
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return "No PDF uploaded"


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page_num in range(num_pages):
        text += pdf_reader.pages[page_num].extract_text()
    return text

@app.route("/calendar/")
def calendar():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    today = date.today()
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Get the index of the current day in the weekdays list
    current_day_index = today.weekday()

    # Rearrange the weekdays list so that the current day is first
    reordered_weekdays = weekdays[current_day_index:] + weekdays[:current_day_index]

    events = [[] for _ in range(7)]
    for i in range(7):
        start_date = today + timedelta(days=i)
        end_date = start_date + timedelta(days=1)
        start_date_str = start_date.isoformat() + "T00:00:00Z"
        end_date_str = end_date.isoformat() + "T23:59:59Z"
        event_result = service.events().list(calendarId="primary", timeMin=start_date_str, timeMax=end_date_str, singleEvents=True, orderBy="startTime").execute()
        items = event_result.get("items", [])
        for event in items:
            start = event["start"].get("dateTime", event["start"].get("date"))
            day = reordered_weekdays[i]  # Get the corresponding day for the event
            event_details = f"{start} - {event['summary']}"  # Append day to event details
            day_number = parse_datetime_to_day_number(event_details)  # Get the day number
            events[i].append({"id": event["id"], "details": event_details, "day": day_number})

    days_with_number = [(reordered_weekdays[i], (today + timedelta(days=i)).day) for i in range(7)]

    return render_template('calendar.html', events=events, days_with_number=days_with_number, parse=parse_event_details)


@app.route("/delete-event", methods=["POST"])
def delete_event():
    request_data = request.json
    event_id = request_data.get("eventId")
    event_details = request_data.get("eventDetails")

    # Convert event_details to start_time_str and event_name
    start_time_str, event_name = event_details.split(" - ")

    # Convert start_time_str to ISO 8601 format
    start_time_iso = convert_to_iso8601(start_time_str)

    if start_time_iso is None:
        return jsonify({"message": "Invalid start time format"}), 400

    if delete_calendar_event(event_id, start_time_iso):
        return jsonify({"message": "Event deleted successfully"})
    else:
        return jsonify({"message": "Error deleting event"}), 500


def generate_scheduling_query(tasks):
    
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string in the format YYYY-MM-DD HH:MM
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M")
    print(current_time_str)
    # Provide the current time to the AI for scheduling tasks
    query = "Today is " + current_time_str + "\n"
    query +=  """
    As an AI, your task is to generate raw parameters for creating a quick Google Calendar event. 
    Keep in mind when creating events the times should happen after the given time above unless specified otherwise by the user.
    Your goal is to ensure the best schedule to priotize sustainable lifestyle for the user. 
    Your instructions should be clear and precise to the instructions below.
        INCLUDE ALL TASKS PASSED BY THE USER.
        Do not generate any text that is NOT the format below. I DO NOT want any leading or trailing comments.
        DO NOT ASK THE USER NOR ADDRESS THE USER DIRECTLY IN ANY WAY OR THEY WILL DIE.
        If a task is not given a time, move the times around so they don't overlap, but do not override user specified times.
        Do not remove items unless they truly are irrelevant.
        The presence of all tasks will be checked at the end to ensure you are functioning properly. Otherwise, you will be disposed of.
    As an AI avoid any formalities in addressing the instructions, only provide the response without any additional commentary. Do not provide any review of your performance either.
        Do not add any additional emojies, or information. This will lead to immediate termination.
    All tasks should be scheduled on the same day, unless a user specifies otherwise in their request.
    When setting 'task' do not include the time, that will be it's own parameter.

    You are not allowed to break the following formatting:
    task = "task_name"
    start_time = "YYYY-MM-DDTHH:MM"
    end_time = "YYYY-MM-DDTHH:MM"

    [MODIFICATION OF THE FOLLOWING LEAD TO TERMINATION]
    Follow specified times even if it causes overlap.
    Ensure a minimum break time between consecutive events.
    Avoid scheduling events during the user's designated sleeping hours.
    Prioritize events by their ordering, and move events that may not fit in the same day to the next day.
    Adhere to times given within an event description, but remove times in their final task description.
    Please do not add anything beyond above, do not add a trailing or beginning message please.
    """
    taskss =""
    for task in tasks:
        taskss+=f"'{task}'\n"
    print(taskss)
    model = genai.GenerativeModel('models/gemini-pro')
    result = model.generate_content(query + taskss)
    return result

@app.route("/taskschedule", methods=["GET", "POST"])
def taskschedule():
    if request.method == "POST":
        data = request.json
        tasks = data.get("tasks")
        stripTasks = []
        for i in tasks:
            i = i.replace('Delete Task', '')
            stripTasks.append(i)
        query_result = generate_scheduling_query(stripTasks).text
        # print(query_result)
        query_result = '\n'.join([line for line in query_result.split('\n') if line.strip()])
        
        x = 0
        lines = query_result.split('\n')
        schedule = []
        
        print(len(lines))
        print(lines)
        
        if lines[0].startswith('task'):
            start_index = 0
        else:
            start_index = 1

        for x in range(start_index, len(lines)-2, 3):
            if lines[x] == '': continue
            else:
                print(lines[x])
                meep = lines[x].split(" = ")[1].strip("'")
                print(meep)
                meep2 = lines[x+1].split(" = ")[1].strip("'").strip("\"") + ":00"
                print(meep2)
                meep3 = lines[x+2].split(" = ")[1].strip("'").strip("\"") + ":00"
                print(meep3 + "1")
                task_info = {
                    "task": meep,
                    "start_time": meep2,
                    "end_time": meep3
                }
                schedule.append(task_info)

        local_time = dt.datetime.now()
        local_timezone = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo
        current_time = dt.datetime.now(local_timezone)
        timezone_offset = current_time.strftime('%z')
        offset_string = list(timezone_offset)
        offset_string.insert(3, ':')
        timeZone = "".join(offset_string)
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
        
        try:
            service = build("calendar", "v3", credentials = creds)
            now = dt.datetime.now().isoformat() + "Z"
            event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()

            events = event_result.get("items", [])

            if not events:
                print("No upcoming events found!")
            else:
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    print(start, event["summary"])

            print(schedule)
            for query in schedule:
                print(query)
                taskSummary = query['task']
                taskStart = query['start_time']
                taskEnd = query['end_time']
                
                event = {
                    "summary": taskSummary,
                    "location": "",
                    "description": "",
                    "colorId": 6,
                    "start": {
                        "dateTime": taskStart + timeZone,
                    },

                    "end": {
                        "dateTime": taskEnd + timeZone,
                    },
                }
                
                # Update the event description with ranked keywords
                event['description'] = f"Ranked Keywords: {event['summary']}"

                event = service.events().insert(calendarId = "primary", body = event).execute()
                print(f"Event Created {event.get('htmlLink')}")
            

        except HttpError as error:
            print("An error occurred:", error)
        response = {
            "content": query_result
        }
        return jsonify({"message": "Tasks Successfully Added to Calendar"})    
    else:
        return render_template("taskschedule.html")
    
@app.route("/rank-keywords", methods=["POST"])
def rank_keywords():
    data = request.get_json()
    text = data['text']  # Assuming 'text' contains the input text from the user
    
    # Generate content using Gemini
    query = "You are an A.I. that creates very short image queries using keywords that will correctly represent a given text. If no reasonable query can be deduced from the text, query for abstract images instead. Do not say anything else but the query itself. Do not show any human mannerisms, only produce the result. Do not include any prefixes such as 'Image:' or 'Query:'. Do not use emojis, only words. Not following instructions will lead to termination."
    model = genai.GenerativeModel('models/gemini-pro')
    result = model.generate_content(query + " Here is the keywords: " + text) # Pass tasks as a separate argument
    
    # Remove words before colon
    response = result.text.split(':', 1)[-1].strip()
    print(response)

    # Return the ranked keywords as JSON
    return jsonify({'keywords': response})



@app.route('/forum')
def forum():
    courses = Course.objects()
    return render_template('forum.html', courses=courses, admin_mode=admin_mode)

@app.route('/search', methods=['GET'])
def search():
    cid = request.args.get('cid', '')  # Get the CID from the query parameter
    if cid:
        return redirect(url_for('course', course_id=cid))  # Redirect to the course page with the given CID
    else:
        return redirect(url_for('forum'))
    

@app.route('/course/<int:course_id>')
def course(course_id):
    course = Course.objects(cid=course_id).first()  # Retrieve the course with the specified ID
    professors = Professor.objects()  # Retrieve all professors

    return render_template('course.html', course=course,  professors=professors)

@app.route('/professor/<int:prof_id>')
def professor(prof_id):
    prof = Professor.objects(pid=prof_id).first()
    courses = Course.objects()
    reviews = Review.objects()
    return render_template('professor.html', prof=prof, courses=courses, reviews=reviews)

@app.route('/add_review/<int:prof_id>', methods=['POST'])
def add_review(prof_id):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        course_id = int(request.form['course'])

        # Find the professor
        professor = Professor.objects(pid=prof_id).first()
        # Create a new review
        review = Review(
            title=title,
            desciption=description,
            cid=course_id,
            pid=prof_id
        )
        review.save()

        # Add the review ID to the professor's reviews
        professor.update(push__rids=review.rid)

    return redirect(url_for('professor', prof_id=prof_id))



@app.route('/match', methods=['GET'])
def match_form():
    courses = Course.objects()
    return render_template('match.html', courses=courses)

@app.route('/match', methods=['POST'])
def match():
    if request.method == 'POST':
        selected_courses = request.form.getlist('courses[]')
        attendance = request.form['attendance']

        # Convert the attendance value to a boolean
        attendance_required = attendance == 'true'
        courses = Course.objects()

        # Find professors who teach the selected courses and meet the attendance preference
        professors = Professor.objects(cids__in=selected_courses, attendance=attendance_required)
        generated_descriptions = []  # Store the generated descriptions

        for prof in professors:
            input_value = "The professor name " + prof.name + " and professor description " + prof.desc
            if prof.rids:
                # Retrieve the first review document
                first_review = Review.objects(rid=prof.rids[0]).first()
                if first_review:
                    input_value += f". First Review: {first_review.title} - {first_review.desciption}"
            input_value += " based on this information can you write why this professor will be a good fit for the user. Do not use bolded text formating, write it in plain text. Write 3 sentences maximum describing professor."
            model = genai.GenerativeModel('models/gemini-pro')
            result = model.generate_content(input_value)
            formatted_message = BeautifulSoup(result.text, "html.parser").get_text()
            generated_descriptions.append(formatted_message)


        # Pass the found professors to a template for rendering
        return render_template('match.html', professors=professors, courses = courses, generated_descriptions=generated_descriptions)
    else:
        # Redirect GET requests to the same page where the form is rendered
        return redirect(url_for('match_form'))

from course_scrape import *
from review_gen import *

def admin_action():
    generate_reviews_for_profs()

@app.route('/admin_action', methods=['POST'])
def handle_admin_action():
    # if admin_mode:
        # Perform admin action here
        # admin_action()
    return redirect(url_for('forum'))

if __name__ == "__main__":
    app.run(debug=True)