import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import math
import numpy as np

#filename = 'S4310.dat'  FILENAME INCLUDES .DAT
def bezier_y_for_x(x, start, control, end, tolerance=1e-5, max_iterations=100):
    """
    Returns the y-coordinate along a quadratic Bezier curve for a given x-coordinate.
    
    Parameters:
    x (float): The x-coordinate along the Bezier curve.
    start (tuple): The (x, y) coordinates of the start point.
    control (tuple): The (x, y) coordinates of the control point.
    end (tuple): The (x, y) coordinates of the end point.
    tolerance (float): The tolerance for the solution (default is 1e-5).
    max_iterations (int): The maximum number of iterations for the approximation.
    
    Returns:
    float: The corresponding y-coordinate on the Bezier curve.
    """
    # Unpack points
    x0, y0 = start
    x1, y1 = control
    x2, y2 = end

    # Function to calculate Bx(t) for a given t
    def bx(t):
        return (1 - t)**2 * x0 + 2 * (1 - t) * t * x1 + t**2 * x2

    # Function to calculate By(t) for a given t
    def by(t):
        return (1 - t)**2 * y0 + 2 * (1 - t) * t * y1 + t**2 * y2

    # Use binary search to solve for t such that bx(t) is approximately x
    lower, upper = 0.0, 1.0
    for _ in range(max_iterations):
        t = (lower + upper) / 2.0
        xt = bx(t)

        if abs(xt - x) < tolerance:
            # Once we've found t, calculate the corresponding y using by(t)
            return by(t)
        elif xt < x:
            lower = t
        else:
            upper = t

def closest_to_midpoint(upperHalfAirfoilData, arc_aft_point, arc_fore_point):
    # Calculate the midpoint between arc_aft_point and arc_fore_point
    midpoint_x = (arc_aft_point[0] + arc_fore_point[0]) / 2
    midpoint_y = (arc_aft_point[1] + arc_fore_point[1]) / 2

    # Find the point in upperHalfAirfoilData closest to the midpoint
    closest_point = min(
        upperHalfAirfoilData,
        
        key=lambda point: math.sqrt((point[0] - midpoint_x) ** 2 + (point[1] - midpoint_y) ** 2)
    )
    return closest_point

def make_flat_airfoil(filename, arc_aft_x_val, arc_fore_x_val):
    airfoil_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','airfoils',filename)
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
    arc_aft_point = max(upperHalfAirfoilData, key=lambda point: (-abs(point[0] - arc_aft_x_val), point[1]))
    arc_fore_point = max(upperHalfAirfoilData, key=lambda point: (-abs(point[0] - arc_fore_x_val), point[1]))

    center_point = closest_to_midpoint(upperHalfAirfoilData,arc_aft_point,arc_fore_point)


    # Initialize lists to store adjusted data
    x_data_adjusted = []
    y_data_adjusted = []

    # Iterate over the upperHalfAirfoilData and adjust y values based on the closest_point condition
    last_flat_point=[1,0]
    for x, y in upperHalfAirfoilData:
        if x >= arc_aft_point[0] and y > 0: #Create Straight Segment Behind Arc
            # Adjust y based on the linear interpolation formula
            y_adjusted = center_point[1] * ((center_point[0] - x) / (1 - center_point[0])) + center_point[1]
            x_data_adjusted.append(x)
            y_data_adjusted.append(y_adjusted)
            if x < last_flat_point[0]:
                last_flat_point=[x,y_adjusted]
        elif x <= arc_aft_point[0] and x > arc_fore_point[0]:
            y_adjusted=bezier_y_for_x(x, arc_fore_point, center_point, last_flat_point)
            x_data_adjusted.append(x)
            y_data_adjusted.append(y_adjusted)
        else: #maintain other sections of upper camber
            x_data_adjusted.append(x)
            y_data_adjusted.append(y)
    if float(x)==1:
            x_data_adjusted.append(x)
            y_data_adjusted.append(y+0.0001)
    # Append the bottom half data without changes to the adjusted lists
    for x, y in bottomHalfAirfoilData:
        x_data_adjusted.append(x)
        y_data_adjusted.append(y)
        # get all points except those that occur on the top of the airfoil with greater x value than closest[0] point
        # this will create a straight line to the end of the airfoil.
        


    # # Plot
    # plt.plot(data.x, data.y, 'b', marker='.', markeredgecolor='black', markersize=3)  # original airfoil
    # #plt.plot(closest_point[0], closest_point[1], 'bo', markersize=10)
    # plt.plot(x_data_adjusted, y_data_adjusted, 'r', marker='.', markeredgecolor='black', markersize=3)  # modified airfoil
    
    # # Plot settings
    # plt.axis('equal')
    # plt.xlim((-0.05, 1.05))
    # plt.legend(['Original Airfoil', 'Nearest Datapoint to Chosen Value', 'Modified Airfoil'])
    # plt.title("Make Airfoil Flat Script - By Vale R")
    # plt.show()

    # call func to make new .dat file
    newAirfoilName = re.search(r'^(.*?)(?=\.dat)', filename).group(0) + "_" + str(arc_aft_x_val) + "_flat_" + str(arc_fore_x_val) + "_rounded"
    # this re.search will get everything in front of the .dat file not in the directory, which will get the airfoil name  
    create_flat_airfoil_file(x_data_adjusted, y_data_adjusted, newAirfoilName)
    flat_length = math.sqrt((1 - arc_aft_point[0]) ** 2 + arc_aft_point[1] ** 2)
    return (newAirfoilName + ".dat", flat_length)

# Export new .dat file with user input
def create_flat_airfoil_file(x_cleaned, y_cleaned, newAirfoilName):
    newFileName = "airfoils/" + newAirfoilName + ".dat"
    f = open(newFileName, "w")
    f.write("# " + newAirfoilName + "\n\n")  # add hash to first line to limit XFOIL errors
    for i in range(len(x_cleaned)):
        coordinateLine = format(x_cleaned[i], '.5f') + " " + format(y_cleaned[i], '.5f')  # round to 5 decimal points
        # X and Y coordinates will be deliminated by " " character.
        f.write(coordinateLine + "\n")

