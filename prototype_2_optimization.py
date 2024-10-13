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

#Constants
g= 9.81 #acceleration of gravity
rho = 1.225 #air_denisty kg m^-3
pi = math.pi

# Aircraft Parameters
m = 1.5 #mass of aircraft (1.5 kg goal)
wingspan = 2.24 #Wingspan (m)
chordlen = 0.28 #chord length (m)
hstab_span = 0.7 #horizontal stabilizer span (m)
hstab_chordlen = 0.14 #horizontal stabilizer chord length (m)
oswald = 0.81059 # Wing Oswald Factor from https://calculator.academy/oswald-efficiency-factor-calculator/
oswald_hs = 0.86912 # Hor Stab Oswald Factor from https://calculator.academy/oswald-efficiency-factor-calculator/
cm_cp = 0.05 #Distance from Cm to Cp (m)

#initialize variables for different airfoils
def init_s4310():
    global CD0,Cl_wing,Cl_hstab
    CD0 = 0.0281# http://www.airfoiltools.com/polar/details?polar=xf-s4310-il-100000
    Cl_wing = 0.4348 #http://www.airfoiltools.com/polar/details?polar=xf-s4310-il-100000
    Cl_hstab = 0.1567 #http://www.airfoiltools.com/polar/details?polar=xf-s4310-il-50000

def init_ag35():
    global CD0,Cl_wing,Cl_hstab
    CD0 = 0.01310# http://www.airfoiltools.com/polar/details?polar=xf-s4310-il-100000
    Cl_wing = 0.4515 #http://www.airfoiltools.com/polar/details?polar=xf-s4310-il-100000
    Cl_hstab = 0.3501 #http://www.airfoiltools.com/polar/details?polar=xf-s4310-il-50000


#Derived
S = wingspan * chordlen #Wing Area
AR = wingspan/chordlen  # Aspect Ratio
S_hs = hstab_span * hstab_chordlen
AR_hs = hstab_span / hstab_chordlen
#ratio of lift from horizontal stabilizer to wing



def get_best_glide(m=m,g=g,rho=rho,S=S,AR=AR,oswald=oswald,CD0=CD0):
    num = 2*m*g
    denom = rho*S*math.sqrt(pi*AR*oswald*CD0) 
    return math.sqrt(num/denom) #analytical minimum of induced+parasite drag eqns

def get_lift(v,Cl,m=m,g=g,rho=rho,S=S):
    lift_force = Cl * rho * 0.5 * v**2 * S # Lift equation
    return lift_force

def get_drag(v,m=m,g=g,rho=rho,S=S,wingspan=wingspan,oswald=oswald,CD0=CD0):
    num= (m * g)**2
    denom = rho/2 * v**2 * pi * wingspan**2 * oswald
    D= rho/2 * v**2 * S * CD0 + num/denom #sum of parasite and induced drag at given airspeed
    return D

def get_power(v,m_input=m):
    return(v*get_drag(v,m=m_input)) #P=V*D

def approx_min_sink(m_input):
    #Approximate minimum power required to maintain altitude at various airspeeds
    min_power=1000
    min_v = None
    for v in np.linspace(0.001,10,10000):
        power = get_power(v,m_input=m_input)
        if power < min_power:
            min_power=power
            min_v = v
    return min_v,min_power 

def hstab_pos_and_params(v_init = approx_min_sink(m)[0]):
    # horizaontal stabilizer distance to center of mass (cm_hstab) depends on the ratio of lift from the wing to the h. stab. (l_ratio)
        #influenced by m_eff (wing must produce more lift to overcome downforce from h. stab.), and optimum velocity
        #These are interdependent, so they are iterated to convergence
    #based on cm_hstab and dependent parameters, flight and power optima are recalculated

    
    ratio_delta = 1.5 #Initialize to above threshold 
    l_ratio_prev= 10
    m_eff = m
    while abs(1-ratio_delta) > 0.01: #Iteratively calculate lift ratio and dependent parameters
        #Converges quickly due to discrete nature of v_min_sink
        v_min_sink,_ = approx_min_sink(m_eff)
        hstab_lift = get_lift(v_min_sink,Cl_hstab,m=m,g=g,rho=rho,S=S_hs)
        l_ratio =  get_lift(v_min_sink,Cl_wing,m=m_eff,g=g,rho=rho,S=S)/hstab_lift #uses previous iteration's m_eff
        m_eff = m + hstab_lift/g
        ratio_delta = l_ratio/l_ratio_prev
        l_ratio_prev = l_ratio
        
    cm_hstab = cm_cp * l_ratio #product of forces and moment arms should be equal
    return cm_hstab, v_min_sink, m_eff, l_ratio

def main():
    init_s4310() #load airfoil-relevant data


    #Return design and flight parameters based on values in the AIRCRAFT PARAMETERS section
    print("The optimal distance from Cm to Cp of Hor. Stab is: "+ str(round(hstab_pos_and_params()[0],3))+' m')
    print("Based on:")
    print("Minimum Sink Velocity: "+str(round(hstab_pos_and_params()[1],3))+" m/s")
    print("Effective Mass: "+str(round(hstab_pos_and_params()[2],3))+' kg')
    print("Wing/Hor. Stab lift ratio: "+ str(round(hstab_pos_and_params()[3],3)))
    print("Power Consumption: "+str(round(get_power(hstab_pos_and_params()[1]),3))+" W")

main()