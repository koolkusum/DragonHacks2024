from os import path, urandom
import os
import certifi
from dotenv import load_dotenv
import random
from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)
app.secret_key = urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")
client = MongoClient(MONGODB_URL, tlsCAFile=certifi.where())


try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
if __name__ == "__main__":
    app.run(debug=True)