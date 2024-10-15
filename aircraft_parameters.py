import os

def oswald(AR):
    #https://calculator.academy/oswald-efficiency-factor-calculator/
    return 1.78 * (1- 0.045 * AR**0.68) -0.64

#Defined
m = 2.5 #mass of aircraft (1.5 kg goal)
wingspan = 2.5 #Wingspan (m)
chordlen = 0.28 #chord length (m)
hstab_span = 0.7 #horizontal stabilizer span (m)
hstab_chordlen = 0.14 #horizontal stabilizer chord length (m)
cm_cp = 0.05 #Distance from Cm to Cp (m)
wing_airfoil_filename = "S4310.dat" #.DAT file for wing airfoil
hstab_airfoil_filename = "S4310.dat" #.DAT file for horizontal stabilizer airfoil

#Derived
S = wingspan * chordlen #Wing Area
AR = wingspan/chordlen  # Aspect Ratio
S_hs = hstab_span * hstab_chordlen
AR_hs = hstab_span / hstab_chordlen
oswald_wing = oswald(AR)
oswald_hs = oswald(AR_hs)
wing_airfoil_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),wing_airfoil_filename)
hstab_airfoil_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),hstab_airfoil_filename)