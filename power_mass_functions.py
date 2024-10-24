def compute_battery_mass(time_of_flight, power_from_solar_panels, Total_Power):
    Wh_needed = Total_Power * time_of_flight
    Wh_generated = power_from_solar_panels * time_of_flight
    total_Wh = Wh_needed - Wh_generated
    battery_mass = total_Wh / 250 #Batter energy density is Wh/kg
    return battery_mass #in kg

def compute_total_mass(static_mass, battery_mass):
    return static_mass + battery_mass