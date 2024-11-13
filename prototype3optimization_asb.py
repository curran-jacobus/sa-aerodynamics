import aerosandbox as asb
import aerosandbox.numpy as np
import neuralfoil as nf
import pandas as pd
import math
import shapely
import numpy



def get_solar_panel_power_weight(wing_span, chordlength):
    panels = wing_span/solar_panel_size*chordlength/solar_panel_size
    weight = panels * solar_panel_mass *g
    power = panels * solar_panel_size**2 * sp_power
    return power,weight

def get_airfoil_area(airfoilfile):
    df = pd.read_csv(airfoilfile, sep='\s+', skiprows=1, header=None, names=['x', 'y'])
    df['x'] = df['x']
    df['y'] = df['y'] 
    coordinates = list(df.itertuples(index=False, name=None))
    cross_section_shape = shapely.Polygon(coordinates)
    
    #Find Volume, Weight from Cross Sectional Area, Wingspan, Foam Density
    cross_sectional_area= cross_section_shape.area
    return(cross_sectional_area)


opti = asb.Opti()  # initialize an optimization environment

## Constants
g= 9.81 #acceleration of gravity
viscosity = 1.78e-5  # viscosity of air [kg/m/s]
density = 1.23  # density of air [kg/m^3]
pi = np.pi
sp_power = 173.2 #W/M2 energy generated per solar panel. 
foam_density = 30.2# Pink Insulation Foam Density kg/m^3
solar_panel_mass = 0.001 #Mass (kg) per solar panel (incl solder)
solar_panel_size = 0.125 #solar panel size (m)

##Aircraft Parameters
weight_fuselage = 30 #Fuselage weight newtons
cm_cp_distance = 0.05
wing_aoa = 3 #Wing aoa (degrees)
drag_area_fuselage = 0.0001 #fuselage fontal area (m^2)
flat_legth_percent = 0.83 #ratio of flat length to chordlength
airfoilfile = "C:\\Users\\curra\\Documents\\Freshman\\Solar_Airplane\\Prototype 3\\prototype3_foil.dat"
airfoil_area = get_airfoil_area(airfoilfile)

CD0=0.01195

##Variables
wingspan = opti.variable(init_guess=3)
chordlen = opti.variable(init_guess=0.5)
airspeed = opti.variable(init_guess=10)  # cruising speed [m/s]
weight = opti.variable(init_guess=50)  # total aircraft weight [N]

##Derived
aspect_ratio=wingspan/chordlen
wing_area=wingspan*chordlen
CL = 0.108*wing_aoa+0.137
Re = (density / viscosity) * airspeed * (wing_area / aspect_ratio) ** 0.5
oswald = 1.78 * (1- 0.045 * aspect_ratio**0.68) -0.64
dynamic_pressure = 0.5 * density * airspeed ** 2

CD_fuselage = drag_area_fuselage / wing_area
CD_parasite =  wing_area * CD0
CD_induced = CL ** 2 / (np.pi * aspect_ratio * oswald)
CD = CD_fuselage + CD_parasite + CD_induced
dynamic_pressure = 0.5 * density * airspeed ** 2
drag = dynamic_pressure * wing_area * CD
lift_cruise = dynamic_pressure * wing_area * CL

##Weight Dependency
_,sp_weight = get_solar_panel_power_weight(wingspan,chordlen)
foam_weight = airfoil_area * chordlen**2 *wingspan * foam_density * g
##Power Relationship
power_produced, _ = get_solar_panel_power_weight(wingspan,chordlen)
power_used = airspeed*drag
power_ratio = power_produced / power_used

##Constraints
opti.subject_to(wingspan <= 3)
opti.subject_to(weight <= lift_cruise)
opti.subject_to(weight == sp_weight + foam_weight+weight_fuselage)
opti.subject_to(power_produced > power_used)

#Objective
opti.maximize(power_ratio)

sol = opti.solve(max_iter=100)

for value in [
    "power_ratio",
    "power_used",
    "power_produced",
    "airspeed",
    "weight",
    "wingspan",
    "chordlen",
]:
    print(f"{value:10} = {sol(eval(value)):.6}")