### VTail Preliminary Analysis
### Curran and Vale January 2024

import aerosandbox as asb
import aerosandbox.numpy as np
import neuralfoil as nf
import pandas as pd
import shapely
import math

##User Defined Functions
def calc_CD0_regression(airfoilfile, re_list=np.linspace(1e5,1e6,10)):
    def fit_power_law(x, y):
        #power law was found to fit CD0 vs Re regressions very well r^2 >0.99 for 5 airfoils. Curran Jacobus 12/1/2024
        if len(x) != len(y):
            raise ValueError("x and y must have the same length.")
        
        # Convert to numpy arrays for easier manipulation
        x = np.array(x)
        y = np.array(y)
        
        if np.any(x <= 0) or np.any(y <= 0):
            raise ValueError("All x and y values must be positive for logarithmic fitting.")
        
        # Take the logarithm of x and y
        log_x = np.log(x)
        log_y = np.log(y)
        
        # Perform linear regression in log-log space
        A = np.vstack([log_x, np.ones_like(log_x)]).T
        coeffs, _, _, _ = np.linalg.lstsq(A, log_y, rcond=None)
        
        # Extract the coefficients
        expo_factor = coeffs[0]
        log_prefactor = coeffs[1]
        prefactor = np.exp(log_prefactor)
        
        return float(prefactor), float(expo_factor)

    def lin_interpolate_CD0(df):
        #Linear Interpolates Coefficient of Drag for when Coefficient of Lift is 0 (CD0)

        # Sort by CL in ascending order to ensure proper interpolation
        df = df.sort_values(by='CL').reset_index(drop=True)

        # Find the indices of the CL values just below and above 0
        cl_below = df[df['CL'] < 0].iloc[-1]  # Last value where CL < 0
        cl_above = df[df['CL'] > 0].iloc[0]   # First value where CL > 0

        # Extract the CL and CD values for interpolation
        cl1, cd1 = cl_below['CL'], cl_below['CD']
        cl2, cd2 = cl_above['CL'], cl_above['CD']

        # Perform linear interpolation for CD when CL = 0
        cd_at_cl_zero = cd1 + (0 - cl1) * (cd2 - cd1) / (cl2 - cl1)

        return cd_at_cl_zero

    def get_CD0(reynolds,airfoil_filepath=airfoilfile):
        #Returns three key airfoil parameters in a dictionary

        #Calculate aerodynamic parameters over range of AoA values, saves to dataframe
        aero_data=pd.DataFrame({"Alpha": [], 'CL': [], 'CD': []})
        for aoa in np.arange(-15,15,0.5):
            data_alpha = nf.get_aero_from_dat_file(
                filename=airfoil_filepath,
                alpha=aoa,
                Re = reynolds,
                model_size='xlarge')
            aero_data_row = pd.DataFrame({"Alpha": [aoa], 'CL': [data_alpha["CL"]], 'CD': [data_alpha["CD"]]})
            aero_data=pd.concat([aero_data,aero_data_row])
        #Desired Values Extracted from Data Frame
        CD0 = lin_interpolate_CD0(aero_data)
        return CD0
    
    cd0_list=[]
    for re in re_list:
        cd0_list.append(get_CD0(re,airfoilfile))
    
    prefactor,expofactor = fit_power_law(re_list,cd0_list)
    return prefactor,expofactor
def get_solar_panel_power_weight(wing_span, chordlength):
    panels = wing_span/solar_panel_size*chordlength/solar_panel_size
    weight = panels * solar_panel_mass *g
    power = panels * solar_panel_size**2 * sp_power
    return power,weight

## Constants
g= 9.81 #acceleration of gravity
viscosity = 1.78e-5  # viscosity of air [kg/m/s]
density = 1.23  # density of air [kg/m^3]
pi = np.pi
sp_power = 173.2 #W/M2 energy generated per solar panel. 
foam_density = 30.2# Pink Insulation Foam Density kg/m^3
solar_panel_mass = 0.001 #Mass (kg) per solar panel (incl solder)
solar_panel_size = 0.125 #solar panel size (m)

## Aircraft Parameters
nontail_weight = 50 #n
wing_airfoil_file = "C:\\Users\\curra\\Documents\\Freshman\\Solar_Airplane\\Prototype 3\\airfoils\\NACA23012.dat" 
wing_aoa = 4.0
wingspan = 3.0
wing_chordlen = 0.34
tail_neutral_airfoil_file = "C:\\Users\\curra\\Documents\\Freshman\\Solar_Airplane\\V Tail\\NACA 0010 Neutral.dat"
tail_up_airfoil_file = "C:\\Users\\curra\\Documents\\Freshman\\Solar_Airplane\\V Tail\\NACA 0010 Up.dat"
tail_down_airfoil_file = "C:\\Users\\curra\\Documents\\Freshman\\Solar_Airplane\\V Tail\\NACA 0010 Down.dat"
tail_aoa = -3
tail_span = 1
tail_chordlen = 0.2
tail_dihedral = 30 
fuselage_frontal_area = 0.010834279 #fuselage frontal area m^2
fuselage_length = 0.3623 #m 
mean_fuselage_diameter = 0.130 #m
fuselage_length = 0.52 #m
cg_ac_distance = 0.1 #m
ac_cpwing_distance = 0.03#m
ac_cptail_distance = 1.2#m

##Calculated Parameters
cd0_prefactor_wing, cd0_expofactor_wing = calc_CD0_regression(wing_airfoil_file)
cd0_prefactor_tailn, cd0_expofactor_tailn = calc_CD0_regression(tail_neutral_airfoil_file)
cd0_prefactor_tailu, cd0_expofactor_tailu = calc_CD0_regression(tail_up_airfoil_file)
cd0_prefactor_taild, cd0_expofactor_taild = calc_CD0_regression(tail_down_airfoil_file)

##Variables
opti = asb.Opti()  #BEGIN OPTI ENV
airspeed = opti.variable(init_guess=10) 
tail_aoa = opti.variable(init_guess=-3)
tail_span = opti.variable(init_guess=1)
tail_chordlen = opti.variable(init_guess=0.2)
tail_dihedral = opti.variable(init_guess=30)

##Derived
dynamic_pressure = 0.5 * density * airspeed ** 2 

##Wing
wing_aspect_ratio=wingspan/wing_chordlen
wing_area=wingspan*wing_chordlen
Re_wing = (density / viscosity) * airspeed * wing_chordlen
wing_oswald = 1.78 * (1- 0.045 * wing_aspect_ratio**0.68) -0.64

CL_wing = nf.get_aero_from_dat_file(
                filename=wing_airfoil_file,
                alpha=wing_aoa,
                Re=Re_wing,
                model_size='xlarge'
            )["CL"]
CD_wing = nf.get_aero_from_dat_file(
                filename=wing_airfoil_file,
                alpha=wing_aoa,
                Re=Re_wing,
                model_size='xlarge'
            )["CD"]

CD0_wing= cd0_prefactor_wing * (Re_wing ** cd0_expofactor_wing)
drag_parasite_wing =  wing_area * CD0_wing *dynamic_pressure
drag_induced_wing = wing_area * dynamic_pressure * CL_wing ** 2 / (np.pi * wing_aspect_ratio * wing_oswald)

#Tail Neutral - TAILS SIMULATED AS IS, NOT FLIPPED SINCE SYMMETRICAL FOILS-- IF CHANGED, CHANGE LIFT SIGN IN DRAG/LIFT TOTALS
tail_aspect_ratio=tail_span/tail_chordlen
tail_area=tail_span*tail_chordlen
Re_tail = (density / viscosity) * airspeed * tail_chordlen
tail_oswald = 1.78 * (1- 0.045 * tail_aspect_ratio**0.68) -0.64

CL_tailn = nf.get_aero_from_dat_file(
                filename=tail_neutral_airfoil_file,
                alpha=tail_aoa,
                Re=Re_tail,
                model_size='xlarge'
            )["CL"]
CD_tail_n = nf.get_aero_from_dat_file(
                filename=tail_neutral_airfoil_file,
                alpha=tail_aoa,
                Re=Re_tail,
                model_size='xlarge'
            )["CD"]

CD0_tailn= cd0_prefactor_tailn * (Re_tail ** cd0_expofactor_tailn)
drag_parasite_tailn =  tail_area * CD0_tailn*dynamic_pressure
drag_induced_tailn = tail_area * dynamic_pressure * CL_tailn ** 2 / (np.pi * tail_aspect_ratio * tail_oswald)

#Fuselage Drag
Re_fuselage = (density / viscosity) * airspeed * fuselage_length
form_factor = 1+60/((fuselage_length/mean_fuselage_diameter)**3) + 0.0025*fuselage_length/mean_fuselage_diameter
skin_friction_coefficient = 0.455/(np.log(Re_fuselage)**2)
CD_fuselage = form_factor *skin_friction_coefficient
drag_fuselage = dynamic_pressure * fuselage_frontal_area * CD_fuselage

##Drag/lift Totals
total_drag = drag_fuselage +drag_parasite_wing +drag_induced_wing + 2* (drag_induced_tailn+drag_induced_tailn)
wing_lift = dynamic_pressure * wing_area * CL_wing
tail_lift = dynamic_pressure * tail_area * 2* CL_tailn * np.cos(tail_dihedral*pi/180)
total_lift = wing_lift+tail_lift #CHANGE + to - if using nonsymmetrical airfoils

##Power
power_out = airspeed * total_drag
power_produced_wing, _ = get_solar_panel_power_weight(wingspan,wing_chordlen)
flat_power_half_tail, _ = get_solar_panel_power_weight(tail_span,tail_chordlen)
power_produced_tail = 2* flat_power_half_tail * np.cos(tail_dihedral * pi/180)
power_in= power_produced_wing + power_produced_tail
power_ratio = power_in/power_out

##Weight
tail_weight =  2 * 1.30 * tail_span
total_weight =  nontail_weight + tail_weight

##Longitudinal Static Stability
forward_moment = total_weight * cg_ac_distance
rear_moment = -1 * (wing_lift*ac_cpwing_distance +tail_lift*ac_cptail_distance)
moment_ratio = forward_moment/rear_moment


## Contstraits 
opti.subject_to(total_lift>=total_weight)
opti.subject_to(power_ratio>=1)
opti.subject_to(tail_dihedral>=10)
opti.subject_to(tail_dihedral<=80)
opti.subject_to(tail_span<=1)
opti.subject_to(tail_span>=0)
opti.subject_to(tail_aoa>=-5)
opti.subject_to(tail_aoa<=5)
opti.subject_to(tail_chordlen >= 0.15)
opti.subject_to(airspeed <= 30)
opti.subject_to(moment_ratio >=1)
opti.subject_to(moment_ratio <= 1.1)

##Objective
opti.maximize(power_ratio)

sol = opti.solve(max_iter=500)

for value in [
    "airspeed",
    "tail_span",
    "tail_aoa",
    "tail_chordlen",
    "tail_dihedral",
    "moment_ratio",
]:
    print(f"{value:10} = {sol(eval(value)):.6}")