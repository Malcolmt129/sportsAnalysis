import requests
import sqlite3
import dotenv
import os



dotenv.load_dotenv("api.env")
api_key = os.getenv("API_KEY")


def getTeams():
    
    conn: sqlite3.Connection = sqlite3.connect("sports.db")
    cursor: sqlite3.Cursor = conn.cursor()


    #Get the data from Rapid Api endpoint
    url = "https://nfl-api-data.p.rapidapi.com/nfl-team-listing/v1/data"

    headers = {
        "x-rapidapi-key":api_key,
        "x-rapidapi-host": "nfl-api-data.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers) 

    if response.status_code == 200:


        #Organize the data to parts that I'll use.
        
        for team in response.json():

            name: str = team["team"]["name"]
            idNum: int = team["team"]["id"]

            #Put that data into the database
            cursor.execute("""
                           INSERT INTO teams (id, team_name)
                           VALUES(?,?)""",
                           (idNum, name))
        
            conn.commit()
    else:
            print("Failed to fetch data from RadidAPI: ", response.status_code, response.text)

    

    conn.close()
    #return some of that data so that it satisfies the requirement of being a router endpoint.
    return response.json()

