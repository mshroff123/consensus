import json

string = json.dumps({"claims": ["Pike Place Market", "Take the ferry to Bainbridge Island", "Spend a day on Lake Washington", "Chihuly Museum", "EMP Museum", "Seattle Aquarium"]})

item = json.load(string)

print(item)