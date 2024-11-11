import requests
import sqlite3
import dotenv
import os
from contextlib import contextmanager #look this up if you don't understand in the future


dotenv.load_dotenv("api.env")
api_key = os.getenv("API_KEY")


@contextmanager
def get_db_connection(db_name: str="sports.db"):
    conn = sqlite3.connect(db_name)

    try: 
        yield conn

    finally:
        conn.close()



# Creates all of the tables needed to store the data that I'll need to find players and teams
# for querying later on.

def init_db():
    with get_db_connection() as conn:
        
        conn.execute('''
                   CREATE TABLE IF NOT EXISTS teams(
                        id INTEGER PRIMARY KEY,
                        team_name TEXT)
                    ''')
        

        conn.execute('''
                    CREATE TABLE IF NOT EXISTS units(
                        unit_id INTEGER PRIMARY KEY, 
                        type TEXT NOT NULL)

                     ''')
        
        conn.execute(''' 
                    CREATE TABLE IF NOT EXISTS  players(
                        team_id INTEGER REFERENCES teams(id) ON UPDATE CASCADE ON DELETE CASCADE,
                        player_id INTEGER,
                        first_name TEXT, 
                        last_name TEXT,
                        full_name TEXT,
                        height INTEGER,
                        weight INTEGER,
                        age INTEGER,
                        number TEXT,
                        experience INTEGER,
                        unit TEXT) 
                   ''')

        conn.commit()



def fillInTeamUnitsTable():


    url = "https://nfl-api-data.p.rapidapi.com/nfl-player-listing/v1/data"

    querystring = {"id":"22"}

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "nfl-api-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:

        response = response.json() # Only need the json response for here on out
        

        units: list = []
        
        for items in response["athletes"]:
            units.append(items["position"])

        
        with get_db_connection() as conn:
           
            count = 1
            for unit in units:
                conn.execute('''
                                INSERT INTO units (unit_id, type) VALUES(?,?)''', (count,unit))
                conn.commit()
                count = count+1
    else:
        print("Failed to fetch data from RadidAPI: ", response.status_code, response.text)




# Add the players info into the database

def addPlayersToDB():
    
    with get_db_connection() as conn:
        teams = conn.execute('''
                     SELECT * FROM teams ''')

        for row in teams:
            url = "https://nfl-api-data.p.rapidapi.com/nfl-team-roster"

            querystring = {"id":str(row[0])}

            headers = {
                "x-rapidapi-key":api_key,
                "x-rapidapi-host": "nfl-api-data.p.rapidapi.com"
            }

            response = requests.get(url, headers=headers, params=querystring)

            if response.status_code == 200:
                response_data = response.json()


                for athlete in response_data.get("athletes", []):
                    
                    experience = athlete.get("experience")["years"]

                    player_data = (row[0],
                                   athlete.get("id"),
                                   athlete.get("firstName"),
                                   athlete.get("lastName"),
                                   athlete.get("fullName"),
                                   athlete.get("height"),
                                   athlete.get("weight"),
                                   athlete.get("age"),
                                   athlete.get("jersey"),
                                   experience, 
                                   athlete.get("position")
                                   )
                                 
                    conn.execute(''' INSERT INTO players (team_id, 
                                                         player_id,
                                                         first_name,
                                                         last_name,
                                                         full_name,
                                                         height,
                                                         weight,
                                                         age,
                                                         number,
                                                         experience,
                                                         unit 
                                                         ) VALUES(?,?,?,?,?,?,?,?,?,?,?)''', player_data)
                    conn.commit()

            else:

                print("Failed to fetch data from RadidAPI: ", response.status_code, response.text)

            
    # Create a database player entry for each player

    

    



        






# Create a function gets the players from a specific team



#Create a function that gets players stats



def getTeamsFromApi():
    
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



if __name__ == "__main__":
    init_db() 
    addPlayersToDB()
