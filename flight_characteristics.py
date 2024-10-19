import aerodynamic_functions
import aircraft_parameters
import airfoils


def get_flight_characteristics():

    #Initialize Reynolds Numbers (These values have been sufficiently convergent)
    wing_re_initial = 100000
    hstab_re_initial = 50000
    ratio = 0 


    while abs(1-ratio) > 0.01:
        #Get Aerodynamic Data for Wing and Horizontal Stabilizers
        wing_airfoil = airfoils.get_CD0_Cl_Cd(aircraft_parameters.wing_airfoil_filepath,wing_re_initial,0)
        hs_airfoil = airfoils.get_CD0_Cl_Cd(aircraft_parameters.hstab_airfoil_filepath,hstab_re_initial,-1*aircraft_parameters.hstab_aoa)
        
        #Calculate Performance Values
        cm_hstab, v_min_sink, m_eff, l_ratio, power = aerodynamic_functions.hstab_pos_and_params(wing_airfoil,hs_airfoil)
        
        #Update Reynolds Numbers
        wing_re_new = aerodynamic_functions.get_reynolds(v_min_sink,aircraft_parameters.chordlen)
        hstab_re_new = aerodynamic_functions.get_reynolds(v_min_sink,aircraft_parameters.hstab_chordlen)

        #Check Convergence
        ratio = wing_re_new/wing_re_initial

        #Update Values
        wing_re_initial = wing_re_new
        hstab_re_initial = hstab_re_new

    return cm_hstab, v_min_sink, m_eff, l_ratio, power, wing_re_new, hstab_re_new
