import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import math

#filename = 'S4310.dat'  FILENAME INCLUDES .DAT

def make_flat_airfoil(filename,flatAfterXValue):
    airfoil_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'airfoils',filename)
    data = pd.read_table(airfoil_filepath, sep='\s+', skiprows=[0], names=['x', 'y'], index_col=False)
    # perform operation on data to get a list of tuples
    xy_data = list(zip(data['x'], data['y']))
    #flatAfterXValue = float(input("Please enter how far along the x-axis (from 0 to 1) the flat surface should start: "))
    upperHalfAirfoilData = [(x, y) for x, y in xy_data if y > 0]  # get only points on the top of the airfoil
    closest_point = max(upperHalfAirfoilData, key=lambda point: (-abs(point[0] - flatAfterXValue), point[1]))
    cleaned_data = [(x, y) for x, y in xy_data if x <= closest_point[0] or y <= 0]
    # get all points except those that occur on the top of the airfoil with greater x value than closest[0] point
    # this will create a straight line to the end of the airfoil.
    # Plot
    plt.plot(data.x, data.y, 'b', marker='.', markeredgecolor='black', markersize=3)  # original airfoil
    plt.plot(closest_point[0], closest_point[1], 'bo', markersize=10)
    x_cleaned, y_cleaned = zip(*cleaned_data)
    plt.plot(x_cleaned, y_cleaned, 'r', marker='.', markeredgecolor='black', markersize=3)  # modified airfoil
    # Plot settings
    plt.axis('equal')
    plt.xlim((-0.05, 1.05))
    plt.legend(['Original Airfoil', 'Nearest Datapoint to Chosen Value', 'Modified Airfoil'])
    plt.title("Make Airfoil Flat Script - By Vale R")
    plt.show()
    # Export new .dat file with user input
    airfoil = re.search(r'^(.*?)(?=\.dat)',filename).group(0)
    outputfilename = airfoil+"_"+str(flatAfterXValue)+"_flat"
    newFileName = "airfoils/" + outputfilename + ".dat"
    f = open(newFileName, "w")
    f.write(outputfilename + "\n\n")
    for i in range(len(x_cleaned)):
        coordinateLine = format(x_cleaned[i], '.5f') + "\t" + format(y_cleaned[i], '.5f')  # round to 5 decimal points
        f.write(coordinateLine + "\n")
    
    flat_length = math.sqrt((1-closest_point[0])**2+closest_point[1]**2)
    return(flat_length)
