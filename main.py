import aerodynamic_functions
import aircraft_parameters
import constants
import airfoils


def main():
    wing_re_initial = 100000
    hstab_re_initial = 50000
    ratio = 0 

    while abs(1-ratio) > 0.01:
        wing_airfoil = airfoils.get_CD0_Cl_Cd(aircraft_parameters.wing_airfoil_filepath,wing_re_initial)
        hs_airfoil = airfoils.get_CD0_Cl_Cd(aircraft_parameters.hstab_airfoil_filepath,hstab_re_initial)
        cm_hstab, v_min_sink, m_eff, l_ratio, power = aerodynamic_functions.hstab_pos_and_params(wing_airfoil,hs_airfoil)
        wing_re_new = aerodynamic_functions.get_reynolds(v_min_sink,aircraft_parameters.chordlen)
        hstab_re_new = aerodynamic_functions.get_reynolds(v_min_sink,aircraft_parameters.hstab_chordlen)

        # print("The optimal distance from Cm to Cp of Hor. Stab is: "+ str(round(cm_hstab,3))+' m')
        # print("Based on:")
        # print("Minimum Sink Velocity: "+str(round(v_min_sink,3))+" m/s")
        # print("Effective Mass: "+str(round(m_eff,3))+' kg')
        # print("Wing/Hor. Stab lift ratio: "+ str(round(l_ratio,3)))
        # print("Power Consumption: "+str(round(power,3))+" W")
        # print(" \n Please Ensure Airfoil Parameters are Consistent with:")
        # print("Re (Wing): "+str(round(wing_re_new)))
        # print("Re (Hor. Stab): "+str(hstab_re_new))

        ratio = wing_re_new/wing_re_initial

        wing_re_initial = wing_re_new
        hstab_re_initial = hstab_re_new

    print("Optimal distance from Cm to Cp of Hor. Stab.: "+ str(round(cm_hstab,3))+' m')
    print("Minimum Sink Velocity: "+str(round(v_min_sink,3))+" m/s")
    print("Effective Mass: "+str(round(m_eff,3))+' kg')
    print("Wing/Hor. Stab. lift ratio: "+ str(round(l_ratio,3)))
    print("Power Consumption: "+str(round(power,3))+" W")
    print("Wing Reynolds Number: "+str(round(wing_re_new)))
    print("Hor Stab. Reynolds Number: "+str(round(hstab_re_new)))

    return cm_hstab, v_min_sink, m_eff, l_ratio, power, wing_re_new, hstab_re_new


if __name__ == "__main__":
    main()