import aerodynamic_functions
import aircraft_parameters
import constants
import airfoils

wing_airfoil = airfoils.s4310_wing
hs_airfoil = airfoils.s4310_hs

def main():
    cm_hstab, v_min_sink, m_eff, l_ratio, power = aerodynamic_functions.hstab_pos_and_params(wing_airfoil,hs_airfoil)
    print("The optimal distance from Cm to Cp of Hor. Stab is: "+ str(round(cm_hstab,3))+' m')
    print("Based on:")
    print("Minimum Sink Velocity: "+str(round(v_min_sink,3))+" m/s")
    print("Effective Mass: "+str(round(m_eff,3))+' kg')
    print("Wing/Hor. Stab lift ratio: "+ str(round(l_ratio,3)))
    print("Power Consumption: "+str(round(power,3))+" W")
    print(" \n Please Ensure Airfoil Parameters are Consistent with:")
    print("Re (Wing): "+str(round(v_min_sink*aircraft_parameters.chordlen/constants.kv)))
    print("Re (Hor. Stab): "+str(round(v_min_sink*aircraft_parameters.hstab_chordlen/constants.kv)))
    return cm_hstab, v_min_sink, m_eff, l_ratio, power


if __name__ == "__main__":
    main()