import numpy as np
import pandas as pd
import re

import flight_characteristics
import aircraft_parameters
import aerodynamic_functions


def wing_hstab_area_optimization():
    
    performance_df = pd.DataFrame({"Wingspan":[],"Chordlen":[],"H.S. Span":[],"H.S. Chordlen":[],"Min Power":[],"Prod. Power":[],"Power Ratio":[]})

    for aircraft_parameters.wingspan in np.arange(start=aircraft_parameters.panel_size*1, stop=aircraft_parameters.panel_size*25,step=aircraft_parameters.panel_size):
        for aircraft_parameters.chordlen in np.arange(start=aircraft_parameters.panel_size*1, stop=aircraft_parameters.panel_size*4,step=aircraft_parameters.panel_size):
            for aircraft_parameters.hstab_span in np.arange(start=aircraft_parameters.panel_size*1, stop=aircraft_parameters.panel_size*8,step=aircraft_parameters.panel_size):
                for aircraft_parameters.hstab_chordlen in np.arange(start=aircraft_parameters.panel_size*1, stop=aircraft_parameters.panel_size*4,step=aircraft_parameters.panel_size):
                    _,_,_,_,min_power,_,_ = flight_characteristics.get_flight_characteristics()
                    produced_power = aerodynamic_functions.get_solar_panel_power()
                    power_ratio = produced_power/min_power
                    performance_df_row = pd.DataFrame({"Wingspan":[aircraft_parameters.wingspan],"Chordlen":[aircraft_parameters.chordlen],"H.S. Span":[aircraft_parameters.hstab_span],"H.S. Chordlen":[aircraft_parameters.hstab_chordlen],"Min Power":[min_power],"Prod. Power":[produced_power],"Power Ratio":[power_ratio]})
                    print(performance_df_row)
                    performance_df = pd.concat([performance_df,performance_df_row])
    
    wing_airfoil = re.search(r"(.*)(?=\.dat)",aircraft_parameters.wing_airfoil_filename)
    hstab_airfoil = re.search(r"(.*)(?=\.dat)",aircraft_parameters.hstab_airfoil_filename)
    csv_filename = wing_airfoil+'_'+hstab_airfoil+"_Area_Optimization.csv"
    performance_df.to_csv(csv_filename)
    return performance_df


wing_hstab_area_optimization()