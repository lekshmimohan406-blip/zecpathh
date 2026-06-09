import json
data = {
    "name": "Lekshmi",
    "course": "Python"
}
with open("data.json", "w") as file:
    json.dump(data, file)
print("JSON file created")