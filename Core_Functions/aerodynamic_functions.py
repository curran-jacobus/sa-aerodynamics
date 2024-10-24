from Core_Functions import aircraft_parameters
from Core_Functions import constants

import math
import numpy as np

def get_reynolds(airspeed, chordlen):
    #Returns Reynolds Number of Airflow Around Wing
    return airspeed*chordlen/constants.kv

def get_best_glide(airfoil_dict, mass= aircraft_parameters.m ,wing_area=aircraft_parameters.S,aspect_ratio=aircraft_parameters.AR,oswald=aircraft_parameters.oswald_wing):
    #Returns Best Glide Speed (maximized L/D)
    num = 2*mass*constants.g
    denom = constants.rho*wing_area*math.sqrt(math.pi*oswald*airfoil_dict["CD0"]) 
    return math.sqrt(num/denom) #analytical minimum of induced+parasite drag eqns

def get_lift(airspeed,airfoil_dict,wing_area=aircraft_parameters.S):
    #Returns the lifting force of an airfoil (N)
    lift_force = airfoil_dict["CL"] * constants.rho * 0.5 * airspeed**2 * wing_area # Lift equation
    return lift_force

def get_drag(airspeed,airfoil_dict,mass=aircraft_parameters.m,wing_area=aircraft_parameters.S,wingspan=aircraft_parameters.wingspan,oswald=aircraft_parameters.oswald_wing):
    #Returns drag force (sum of parasitic and induced) (N)
    num= (mass * constants.g)**2
    denom = constants.rho/2 * airspeed**2 * constants.pi * wingspan**2 * oswald
    D= constants.rho/2 * airspeed**2 * wing_area * airfoil_dict["CD0"] + num/denom #sum of parasite and induced drag at given airspeed
    return D

def get_power(airspeed,airfoil_dict,mass=aircraft_parameters.m):
    #Returns power required for flight in ideal conditions
    return(airspeed*get_drag(airspeed,airfoil_dict,mass=mass)) #P=V*D

def approx_min_sink(airfoil_dict, mass):
    #Approximate minimum power required to maintain altitude at various airspeeds
    min_power=1000
    min_v = None
    for v in np.linspace(0.001,10,10000):
        power = get_power(v,airfoil_dict,mass=mass)
        if power < min_power:
            min_power=power
            min_v = v
    return min_v,min_power 

def hstab_pos_and_params(wing_airfoil_dict, hstab_airfoil_dict):
    # horizaontal stabilizer distance to center of mass (cm_hstab) depends on the ratio of lift from the wing to the h. stab. (l_ratio)
        #influenced by m_eff (wing must produce more lift to overcome downforce from h. stab.), and optimum velocity
        #These are interdependent, so they are iterated to convergence
    #based on cm_hstab and dependent parameters, flight and power optima are recalculated

    ratio_delta = 1.5 #Initialize to above threshold 
    l_ratio_prev= 10
    m_eff = aircraft_parameters.m
    while abs(1-ratio_delta) > 0.01: #Iteratively calculate lift ratio and dependent parameters
        #Converges quickly due to discrete nature of v_min_sink
        v_min_sink,_ = approx_min_sink(wing_airfoil_dict,m_eff)
        hstab_lift = get_lift(v_min_sink,hstab_airfoil_dict,wing_area=aircraft_parameters.S_hs)
        l_ratio =  get_lift(v_min_sink,wing_airfoil_dict,wing_area=aircraft_parameters.S)/hstab_lift #uses previous iteration's m_eff
        m_eff = aircraft_parameters.m + hstab_lift/constants.g
        ratio_delta = l_ratio/l_ratio_prev
        l_ratio_prev = l_ratio
        
    cm_hstab = aircraft_parameters.cm_cp * l_ratio #product of forces and moment arms should be equal
    power = get_power(v_min_sink,wing_airfoil_dict, mass=m_eff)
    return float(cm_hstab), float(v_min_sink), float(m_eff), float(l_ratio), float(power)

def get_solar_panel_power(chord_step):
    #Calculates solar panel power (W) based on wing area and constant solar incidence
    wing_area= math.floor(aircraft_parameters.wingspan/aircraft_parameters.panel_size)*math.floor(aircraft_parameters.chordlen/chord_step)* aircraft_parameters.panel_size**2
    hs_area = math.floor(aircraft_parameters.hstab_span/aircraft_parameters.panel_size)*math.floor(aircraft_parameters.hstab_chordlen/aircraft_parameters.panel_size)* aircraft_parameters.panel_size**2
    return (wing_area+hs_area)*constants.sp_power