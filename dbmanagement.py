import requests
import sqlite3
import dotenv
import os
#import time
from contextlib import contextmanager #look this up if you don't understand in the future

import pandas as pd
import numpy as np


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
                        team_name TEXT PRIMARY KEY,
                        id INTEGER 
                        )
                    ''')
        

        conn.execute('''
                    CREATE TABLE IF NOT EXISTS units(
                        unit_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        type TEXT NOT NULL)
 
                     ''')

        conn.execute('''
                    CREATE TABLE IF NOT EXISTS positions(
                        name TEXT UNIQUE,
                        abbreviation TEXT)

                    ''')
        
        conn.execute(''' 
                    CREATE TABLE IF NOT EXISTS  players(
                        team_id TEXT REFERENCES teams(team_name) ON UPDATE CASCADE ON DELETE CASCADE,
                        player_id INTEGER,
                        first_name TEXT, 
                        last_name TEXT,
                        full_name TEXT,
                        height INTEGER,
                        weight INTEGER,
                        age INTEGER,
                        number TEXT,
                        experience INTEGER,
                        position TEXT,
                        unit TEXT) 
                   ''')

        conn.commit()

        #Make a table for different types of stats.








# Add the players info into the database


def addPlayersToDB():
    

    with get_db_connection() as conn:
        teams = conn.execute('''
                     SELECT * FROM teams ''')

        for row in teams:
            url = "https://nfl-api-data.p.rapidapi.com/nfl-player-listing/v1/data"

            querystring = {"id":str(row[1])}

            headers = {
                "x-rapidapi-key":api_key,
                "x-rapidapi-host": "nfl-api-data.p.rapidapi.com"
            }

            response: requests.models.Response = requests.get(url, headers=headers, params=querystring)

            if response.status_code == 200:
                
                response_data: dict = response.json()

                for unit in response_data.get("athletes", []): # returns the value associated with key if exist, if not the default is []
                    unit_type = unit["position"] #Make sure that these team units are put into the database

                    conn.execute(''' INSERT OR IGNORE INTO units (type) VALUES(?)''', (unit_type,))
                    
                    players: list = unit.get("items", []) #Get the list of players
                    

                    for player in players:
                        
                        # Have to get these now so that we can add them to the player_data tuple 
                        position_dict: dict = player.get("position", {})
                        experience_dict: dict = player.get("experience", {}) 
                        
                        #Also we need to add all of the postions into the their table in the database

                        conn.execute(''' INSERT OR IGNORE INTO positions (name, abbreviation) VALUES(?,?)''', (position_dict["name"],position_dict["abbreviation"]))

                        player_data = (
                                        row[0], 
                                        player.get("id"),
                                        player.get("firstName"),
                                        player.get("lastName"),
                                        player.get("fullName"),
                                        player.get("height"),
                                        player.get("weight"),
                                        player.get("age"),
                                        player.get("jersey"),
                                        experience_dict["years"],
                                        position_dict["abbreviation"],
                                        unit_type)
                    
                        conn.execute(''' INSERT OR IGNORE INTO players (team_id, 
                                                         player_id,
                                                         first_name,
                                                         last_name,
                                                         full_name,
                                                         height,
                                                         weight,
                                                         age,
                                                         number,
                                                         experience,
                                                          position,
                                                         unit 
                                                         ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', player_data)
                        conn.commit()

            else:

                print("Failed to fetch data from RadidAPI: ", response.status_code, response.text)



# Create a function gets the players from a specific team

def getTeamPlayers(teamName: str):

    with get_db_connection() as conn:

        players: sqlite3.Cursor = conn.execute("""SELECT player_id, full_name, number, unit, position 
                            FROM players
                            WHERE players.team_id = ?
                            """, (teamName,))
        for row in players:
            print(row)


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
                           INSERT INTO teams (team_name, id)
                           VALUES(?,?)""",
                           (name, idNum))
        
            conn.commit()
    else:
            print("Failed to fetch data from RadidAPI: ", response.status_code, response.text)

    

    conn.close()
    #return some of that data so that it satisfies the requirement of being a router endpoint.
    return response.json()

def getTeamStats(team: str, year: int):
    with get_db_connection() as conn:
        teamName = conn.execute("""
                                SELECT id FROM teams WHERE team_name = ? """, (team,))
        teamID = teamName.fetchone()[0]

        url = "https://nfl-api-data.p.rapidapi.com/nfl-team-statistics"

        querystring = {"year":year,"id":teamID}

        headers = {
            "x-rapidapi-key":api_key,
            "x-rapidapi-host": "nfl-api-data.p.rapidapi.com"
        }

        response: requests.models.Response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code == 200:
           pass 

        else:
            print("Failed to fetch data from RapidaAPI: ", response.status_code, response.text)




def getGameLog(player: str):
    with get_db_connection() as conn:
        playerID = conn.execute(""" SELECT player_id
                       FROM players
                       WHERE full_name = ?""",(player,))

        playerID = playerID.fetchone()[0]
        url = "https://nfl-api-data.p.rapidapi.com/nfl-ath-gamelog"
        
        querystring  = {"id":playerID}
        
        headers = {
                "x-rapidapi-key":api_key,
                "x-rapidapi-host": "nfl-api-data.p.rapidapi.com"
            }

        response: requests.models.Response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:

            response_data: dict = response.json()
            
            labels = response_data.get("names", [])

            if len(labels) > 0:
                
                labels_dict: dict = {i: value for i, value in enumerate(labels)} # Need to get more info such as the 
                                                                                 # date of the game opponent and result
                                                                                 # of the game 

            else:
                print("Failed to retrieve labels")
                return 
            
            # This will be me parsing through the gamelog object... May need to refactor this later 
            season: list = response_data.get("seasonTypes", [])
            current_year: dict = season[0]
            categories: list = current_year.get("categories", [])
            events: list = categories.get("events", []) # Need to parse this to get the Dataframe that I want
            totals: list = categories.get("totals", [])

            games_list = []
            
            # Get the stats of each game....
            for event in events:
                eventID



            gamelog = pd.DataFrame(columns=labels_dict.values()) # This populates the columns with the label names
            
            
            
            

        else:
            print("Falied to fetch data from RapidAPI: ", response.status_code, response.text)



if __name__ == "__main__":

    #getTeamStats("Ravens", 2023)

    getGameLog("Lamar Jackson")
