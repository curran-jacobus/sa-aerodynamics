from Core_Functions.aerodynamic_functions import get_reynolds
import json

# Specify the path to your JSON file
file_path = 'power_params.json'

# Open the JSON file and load it into a Python object
with open(file_path, 'r') as json_file:
    Mass_file = json.load(json_file)



Total_Power = 0
Total_Mass = 0

for component in Mass_file:
    Total_Power += component["voltage"] * component["current"] * (component["duty cycle"] * 0.01) * ((component["contingency"] * 0.01) + 1) * component["count"]
    Total_Mass += component["mass"] * ((component["contingency"] * 0.01) + 1) * component["count"]

print(Total_Power)
print(Total_Mass)
