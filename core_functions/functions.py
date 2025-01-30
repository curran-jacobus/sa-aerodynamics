#Functions


import constants

import pandas as pd
from climlab.solar.insolation import daily_insolation
import os
import numpy as np
import csv

def get_solar_insolation(csv_file):
    with open(os.path.join(os.getcwd(),'..','plane_csvs',csv_file),mode='r') as params:
        reader = csv.reader(params)
        for row in reader:
            if row[0] == "testflight_day":
                day_of_year = row[2]
    average_solar_insolation = daily_insolation(constants.stanford_latitude, day_of_year)
    captured_energy = average_solar_insolation * constants.sp_efficiency
    return(captured_energy)



def get_solar_panel_power_weight(csv_file, airfoil, wing_span):
    panels = wing_span/constants.solar_panel_size*get_upper_camber(airfoil)/constants.solar_panel_size
    weight = panels * constants.solar_panel_mass *g
    power = panels * constants.solar_panel_size**2 * get_solar_insolation(csv_file)
    return power,weight

def get_upper_camber(airfoil):
    
    data = pd.read_table(os.path.join(os.getcwd(),'..',"airfoils", airfoil), sep='\s+', skiprows=[0], names=['x', 'y'], index_col=False)

    # Convert the dataframe to a list of tuples
    xy_data = list(zip(data['x'], data['y']))

    # Initialize previous_x and filter to get only upper half airfoil data (x values that are decreasing)
    previous_x = 1
    split_index = None
    for i, (x, y) in enumerate(xy_data):
        if x > previous_x:
            split_index = i
            break
        previous_x = x

    # Split the data into upper and bottom halves based on the split index
    upperHalfAirfoilData = xy_data[:split_index]
    dist_array = [
        np.sqrt((upperHalfAirfoilData[i][0] - upperHalfAirfoilData[i + 1][0])**2 +
                (upperHalfAirfoilData[i][1] - upperHalfAirfoilData[i + 1][1])**2)
        for i in range(len(upperHalfAirfoilData) - 1)
    ]

    # Sum all distances to get the upper camber length
    upper_camber_length = np.sum(dist_array)
    return(upper_camber_length)