import json
with open(f"./json/database.json", 'r') as file: # Get Bot Token
        db = json.load(file)['playersactivity']
print(db)