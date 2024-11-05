from flask import Flask, jsonify
import requests
import sqlite3
import dotenv
import os






dotenv.load_dotenv("api.env")
api_key = os.getenv("API_KEY")


app = Flask(__name__)


@app.route('/')
def home() -> str:
    return "Hello World!"



# This function will return all of the teams in the NFL and their ID numbers
#@app.route('/teams/listing', methods=['GET'])








def init_db():
    conn: sqlite3.Connection = sqlite3.connect('sports.db')
    cursor: sqlite3.Cursor = conn.cursor() 
   
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS teams(
                        id INTEGER PRIMARY KEY,
                        team_name TEXT)
                  ''')

    conn.commit()
    conn.close()

if __name__ == "__main__": 
    
    pass

