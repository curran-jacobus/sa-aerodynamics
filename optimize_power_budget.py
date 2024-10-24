import aerodynamic_functions
import json
import power_mass_functions as pm
import flight_characteristics

# Specify the path to your JSON file
file_path = 'power_params.json'

# Open the JSON file and load it into a Python object
with open(file_path, 'r') as json_file:
    Mass_file = json.load(json_file)



Total_Power = 0 #initialize
static_mass = 0 #initialize
time_of_flight = 10 #hours
produced_power = aerodynamic_functions.get_solar_panel_power()


for component in Mass_file:
    Total_Power += component["voltage"] * component["current"] * (component["duty cycle"] * 0.01) * ((component["contingency"] * 0.01) + 1) * component["count"]
    static_mass += component["mass"] * ((component["contingency"] * 0.01) + 1) * component["count"]

_,_,_,_,flight_power,_,_ = flight_characteristics.get_flight_characteristics() #computes min power that the motor needs to generate to keep plane in flight

Total_Power = flight_power + Total_Power


battery_mass = pm.compute_battery_mass(time_of_flight, produced_power, Total_Power)
Total_Mass = pm.compute_total_mass(static_mass, battery_mass)
print(Total_Mass, Total_Power)
