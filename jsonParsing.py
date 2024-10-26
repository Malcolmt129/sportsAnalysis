import json



# Make a function that will parse through the teams file and get the id of each teams
# that way we can use the id number to find players.

teamDict = {}

file_path = "./NFLanalysis/output/nfl_team_data.json"
with open(file_path, 'r') as file:
    teamsData = file.read()
    teamsData = json.loads(teamsData)

for team in teamsData:
    teamDict[team["team"]["name"]] = team["team"]["id"]

print(teamDict)

file_path = "./NFLanalysis/output/nfl_team_IDs.json"

with open(file_path, 'w') as file:
    file.write(str(teamDict))
