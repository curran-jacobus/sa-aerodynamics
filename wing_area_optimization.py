import numpy as np
import pandas as pd
import re
import shapely

import flight_characteristics
import aircraft_parameters
import aerodynamic_functions
import constants

def get_wing_weight(airfoilfile, wingspan, chordlen):
    df = pd.read_csv(airfoilfile, sep='\s+', skiprows=1, header=None, names=['x', 'y'])

    
    # Multiply each coordinate by chordlen
    df['x'] = df['x'] * chordlen
    df['y'] = df['y'] * chordlen

    # Convert the DataFrame to a list of tuples (x, y)
    coordinates = list(df.itertuples(index=False, name=None))
    cross_section_shape = shapely.Polygon(coordinates)
    cross_sectional_area= cross_section_shape.area
    volume = cross_sectional_area*wingspan
    wing_mass = volume*constants.foam_density
    return(wing_mass)


def wing_hstab_area_optimization():
    
    performance_df = pd.DataFrame({"Wingspan":[],"Chordlen":[],"H.S. Span":[],"H.S. Chordlen":[],"Min Power":[],"Prod. Power":[],"Power Ratio":[]})
    wingless_mass = aircraft_parameters.m

    for aircraft_parameters.wingspan in np.arange(start=aircraft_parameters.panel_size*1, stop=aircraft_parameters.panel_size*25,step=aircraft_parameters.panel_size):
        for aircraft_parameters.chordlen in np.arange(start=aircraft_parameters.panel_size*1, stop=aircraft_parameters.panel_size*4,step=aircraft_parameters.panel_size):
            for aircraft_parameters.hstab_span in np.arange(start=aircraft_parameters.panel_size*1, stop=aircraft_parameters.panel_size*8,step=aircraft_parameters.panel_size):
                for aircraft_parameters.hstab_chordlen in np.arange(start=aircraft_parameters.panel_size*1, stop=aircraft_parameters.panel_size*4,step=aircraft_parameters.panel_size):
                    aircraft_parameters.m = wingless_mass +get_wing_weight(aircraft_parameters.wing_airfoil_filepath,aircraft_parameters.wingspan,aircraft_parameters.chordlen)+get_wing_weight(aircraft_parameters.hstab_airfoil_filepath,aircraft_parameters.hstab_span,aircraft_parameters.hstab_chordlen)

                    _,_,_,_,min_power,_,_ = flight_characteristics.get_flight_characteristics()
                    produced_power = aerodynamic_functions.get_solar_panel_power()
                    power_ratio = produced_power/min_power
                    performance_df_row = pd.DataFrame({"Wingspan":[aircraft_parameters.wingspan],"Chordlen":[aircraft_parameters.chordlen],"H.S. Span":[aircraft_parameters.hstab_span],"H.S. Chordlen":[aircraft_parameters.hstab_chordlen],"Min Power":[min_power],"Prod. Power":[produced_power],"Power Ratio":[power_ratio]})
                    print(performance_df_row)
                    performance_df = pd.concat([performance_df,performance_df_row])
    
    wing_airfoil = re.search(r"(.*)(?=\.dat)",aircraft_parameters.wing_airfoil_filename)
    hstab_airfoil = re.search(r"(.*)(?=\.dat)",aircraft_parameters.hstab_airfoil_filename)
    csv_filename = wing_airfoil+'_'+hstab_airfoil+"_Area_Optimization.csv"
    performance_df.to_csv(csv_filename)
    return performance_df


wing_hstab_area_optimization()