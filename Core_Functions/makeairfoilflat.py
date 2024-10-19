import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import math

#filename = 'S4310.dat'  FILENAME INCLUDES .DAT

def make_flat_airfoil(filename, flatAfterXValue):
    airfoil_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'airfoils',filename)
    # this will add the airfoils/ directory or use another equivalent string expression if OS differs
    
    data = pd.read_table(airfoil_filepath, sep='\s+', skiprows=[0], names=['x', 'y'], index_col=False)

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
    upperHalfAirfoilData = xy_data[:split_index]  # Data where x is decreasing
    bottomHalfAirfoilData = xy_data[split_index:] 
    # Find the closest point to the flatAfterXValue on the upper half
    closest_point = max(upperHalfAirfoilData, key=lambda point: (-abs(point[0] - flatAfterXValue), point[1]))

    # Initialize lists to store adjusted data
    x_data_adjusted = []
    y_data_adjusted = []

    # Iterate over the upperHalfAirfoilData and adjust y values based on the closest_point condition
    for x, y in upperHalfAirfoilData:
        if x >= closest_point[0] and y > 0:
            # Adjust y based on the linear interpolation formula
            y_adjusted = closest_point[1] * ((closest_point[0] - x) / (1 - closest_point[0])) + closest_point[1]
            x_data_adjusted.append(x)
            y_data_adjusted.append(y_adjusted)
        else:
            # Keep the original x and y
            x_data_adjusted.append(x)
            y_data_adjusted.append(y)

    # Append the bottom half data without changes to the adjusted lists
    for x, y in bottomHalfAirfoilData:
        x_data_adjusted.append(x)
        y_data_adjusted.append(y)
        # get all points except those that occur on the top of the airfoil with greater x value than closest[0] point
        # this will create a straight line to the end of the airfoil.
        


    # Plot
    plt.plot(data.x, data.y, 'b', marker='.', markeredgecolor='black', markersize=3)  # original airfoil
    plt.plot(closest_point[0], closest_point[1], 'bo', markersize=10)
    plt.plot(x_data_adjusted, y_data_adjusted, 'r', marker='.', markeredgecolor='black', markersize=3)  # modified airfoil
    
    # Plot settings
    plt.axis('equal')
    plt.xlim((-0.05, 1.05))
    plt.legend(['Original Airfoil', 'Nearest Datapoint to Chosen Value', 'Modified Airfoil'])
    plt.title("Make Airfoil Flat Script - By Vale R")
    plt.show()

    # call func to make new .dat file
    newAirfoilName = re.search(r'^(.*?)(?=\.dat)', filename).group(0) + "_" + str(flatAfterXValue) + "_flat"
    # this re.search will get everything in front of the .dat file not in the directory, which will get the airfoil name  
    create_flat_airfoil_file(x_data_adjusted, y_data_adjusted, newAirfoilName)
    flat_length = math.sqrt((1 - closest_point[0]) ** 2 + closest_point[1] ** 2)
    return (newAirfoilName + ".dat", flat_length)

# Export new .dat file with user input
def create_flat_airfoil_file(x_cleaned, y_cleaned, newAirfoilName):
    newFileName = "airfoils/" + newAirfoilName + ".dat"
    f = open(newFileName, "w")
    f.write(newAirfoilName + "\n\n")
    for i in range(len(x_cleaned)):
        coordinateLine = format(x_cleaned[i], '.5f') + "\t" + format(y_cleaned[i], '.5f')  # round to 5 decimal points
        f.write(coordinateLine + "\n")

