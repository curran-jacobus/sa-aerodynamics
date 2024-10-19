import numpy as np
import pandas as pd
import re
import shapely
import os

import Core_Functions.flight_characteristics
import Core_Functions.aircraft_parameters
import Core_Functions.aerodynamic_functions
import Core_Functions.constants

def get_wing_weight(airfoilfile, wingspan, chordlen):
    #Get Airfoil Cross Sectional Area from .dat file using shapely package
    df = pd.read_csv(airfoilfile, sep='\s+', skiprows=1, header=None, names=['x', 'y'])
    df['x'] = df['x'] * chordlen
    df['y'] = df['y'] * chordlen
    coordinates = list(df.itertuples(index=False, name=None))
    cross_section_shape = shapely.Polygon(coordinates)
    
    #Find Volume, Weight from Cross Sectional Area, Wingspan, Foam Density
    cross_sectional_area= cross_section_shape.area
    volume = cross_sectional_area*wingspan
    wing_mass = volume*constants.foam_density
    return(wing_mass)

def get_solar_panel_mass():
    wing_panels = aircraft_parameters.wingspan/aircraft_parameters.panel_size * aircraft_parameters.chordlen/aircraft_parameters.panel_size
    hstab_panels = aircraft_parameters.hstab_span/aircraft_parameters.panel_size * aircraft_parameters.hstab_chordlen/aircraft_parameters.panel_size
    return (wing_panels+hstab_panels)*constants.solar_panel_mass

def wing_hstab_area_optimization(chordstep):
    
    #Initialize Dataframe
    performance_df = pd.DataFrame({"Wingspan":[],"Chordlen":[],"H.S. Span":[],"H.S. Chordlen":[],"Min Power":[],"Prod. Power":[],"Power Ratio":[],"Cm-Cp Hor Stab Dist":[],"Min Sink":[],"Eff. Mass":[],"Lift Ratio":[],"Wing Reynolds":[],"Hor Stab Reynolds":[]})
    wingless_mass = aircraft_parameters.m

    total_iterations = 9*5*7*3
    current_iteration = 0
    #Iterate over reasonable wingspans, chordlenths for wing and horizontal stabilizer in solar-panel sized increments
    for aircraft_parameters.wingspan in np.arange(start=aircraft_parameters.panel_size*17, stop=aircraft_parameters.panel_size*25,step=aircraft_parameters.panel_size):
        for aircraft_parameters.chordlen in np.arange(start=chordstep*1, stop=chordstep*5,step=chordstep):
            for aircraft_parameters.hstab_span in np.arange(start=aircraft_parameters.panel_size*4, stop=aircraft_parameters.panel_size*10,step=aircraft_parameters.panel_size):
                for aircraft_parameters.hstab_chordlen in np.arange(start=aircraft_parameters.panel_size*1, stop=aircraft_parameters.panel_size*3,step=aircraft_parameters.panel_size):
                    aircraft_parameters.m = wingless_mass +get_wing_weight(aircraft_parameters.wing_airfoil_filepath,aircraft_parameters.wingspan,aircraft_parameters.chordlen)+get_wing_weight(aircraft_parameters.hstab_airfoil_filepath,aircraft_parameters.hstab_span,aircraft_parameters.hstab_chordlen)+get_solar_panel_mass()

                    #Calculate Power Requirements and Outputs
                    cm_cp_optimum,vminsink_optimum,m_eff_optimum,liftratio_optimum,min_power,wing_reynolds_optimum,hstab_reynolds_optimum = flight_characteristics.get_flight_characteristics()
                    produced_power = aerodynamic_functions.get_solar_panel_power(chordstep)
                    
                    #Ratio of produced power from panels to power reqd to maintain altitude. this is selected for
                    power_ratio = produced_power/min_power
                    
                    #make dataframe row, append to dataframe
                    performance_df_row = pd.DataFrame({"Wingspan":[aircraft_parameters.wingspan],"Chordlen":[aircraft_parameters.chordlen],"H.S. Span":[aircraft_parameters.hstab_span],"H.S. Chordlen":[aircraft_parameters.hstab_chordlen],"Min Power":[min_power],"Prod. Power":[produced_power],"Power Ratio":[power_ratio],"Cm-Cp Hor Stab Dist":[cm_cp_optimum],"Min Sink":[vminsink_optimum],"Eff. Mass":[m_eff_optimum],"Lift Ratio":[liftratio_optimum],"Wing Reynolds":[wing_reynolds_optimum],"Hor Stab Reynolds":[hstab_reynolds_optimum]})
                    performance_df = pd.concat([performance_df,performance_df_row])
                    
                    current_iteration +=1
                    print("Iteration " + str(current_iteration) + " Out of " + str(total_iterations))
    #Get Airfoil Names Using Regex, save to .csv file with airfoils as filename.
    wing_airfoil = re.search(r"(.*)(?=\.dat)",aircraft_parameters.wing_airfoil_filename).group(0)
    hstab_airfoil = re.search(r"(.*)(?=\.dat)",aircraft_parameters.hstab_airfoil_filename).group(0)
    csv_filename = wing_airfoil+'_'+hstab_airfoil+"_Area_Optimization.csv"
    performance_df.to_csv(os.join(__file__,'Optimization_Outputs',csv_filename))
    return performance_df