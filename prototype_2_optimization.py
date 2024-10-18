#October 2024
#Stanford University Flight Club Solar Aiplane Project
#Curran Jacobus

#Description
    #This program contains functions to evaluate airfoil and wing geometry performance in the context of a solar airplane
    #Key uses include calculating the minimum sink airspeed and corresponding power, and position of horizontal stabilizer

#Use
    #Ensure Numpy is imported to the environment
    #Set aircraft parameters and airfoil data
    #call main()


#Key Refs
    #https://calculator.academy/oswald-efficiency-factor-calculator/
    #https://aviation.stackexchange.com/questions/30332/what-determines-the-best-glide-speed/30350#30350

import numpy as np
import math



def main():
    #Return design and flight parameters based on values in the AIRCRAFT PARAMETERS section
    print("The optimal distance from Cm to Cp of Hor. Stab is: "+ str(round(hstab_pos_and_params()[0],3))+' m')
    print("Based on:")
    print("Minimum Sink Velocity: "+str(round(hstab_pos_and_params()[1],3))+" m/s")
    print("Effective Mass: "+str(round(hstab_pos_and_params()[2],3))+' kg')
    print("Wing/Hor. Stab lift ratio: "+ str(round(hstab_pos_and_params()[3],3)))
    print("Power Consumption: "+str(round(get_power(hstab_pos_and_params()[1]),3))+" W")
    print(" \n Please Ensure Airfoil Parameters are Consistent with:")
    print("Re (Wing): "+str(round(hstab_pos_and_params()[1]*chordlen/0.000014207)))
    print("Re (Hor. Stab): "+str(round(hstab_pos_and_params()[1]*hstab_chordlen/0.000014207)))
main()