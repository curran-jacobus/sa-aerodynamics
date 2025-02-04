import csv
import numpy as np
import pandas as pd
import neuralfoil as nf
import aerosandbox as asb
import os
import re
import shapely

import core_functions.constants as constants
import core_functions.functions as functions

csv_file = os.path.join(os.getcwd(),'plane_csvs',"variable_loading_test.csv") #Update this per optimization

opti=asb.Opti()

#Import Aircraft-Dependent Paramters and Variables as Class Attribtutes
class plane_values:
    def __init__(self, csv_file):
        #self._load_params(csv_file)
        self._load_opti_vars(csv_file)
        self._get_wing_volumes()
        self._get_CD0_airfoil_object(csv_file)
        self._check_and_convert_to_float()
    #ensure airfoil is from this list
    #https://github.com/peterdsharpe/AeroSandbox/tree/master/aerosandbox/geometry/airfoil/airfoil_database

    def _load_opti_vars(self, csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                name, type, value, min, max = row
                print(row)
                if type == 'v':
                    if name=='ï»¿span':
                        setattr(self, re.sub(r'[^a-zA-Z_]+', '', name.strip()),opti.variable(init_guess=float(value), lower_bound=float(min), upper_bound= float(max)))
                    else:
                        setattr(self, name.strip(),opti.variable(init_guess=float(value), lower_bound=float(min), upper_bound= float(max)))
                elif type == 'p':
                    if name=="ï»¿span": #FIX THE REGEX
                        setattr(self, re.sub(r'[^a-zA-Z_]+', '', name.strip()),value)
                    else:
                        setattr(self, name.strip(),value)

    def _check_and_convert_to_float(self):
        for attribute in vars(self):
            value = getattr(self, attribute)
            if isinstance(value, str) and value.isdigit():
                setattr(self, attribute, float(value))
            elif isinstance(value, str) and value.replace('.','').isdigit():
                setattr(self, attribute, float(value))



    def _get_CD0_airfoil_object(self, params_csv, cd0_file = "airfoil_cd0_nodat.csv"):
        with open(params_csv) as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0]=='airfoil':
                    df = pd.read_csv(cd0_file)
                    match_row = df[df.iloc[:,0]== str(row[2])] #wing
                    self.wing_cd0_prefactor = match_row.iloc[0,1]
                    self.wing_cd0_expofactor = match_row.iloc[0,2]
                    self.airfoil = asb.Airfoil(row[2])
                elif row[0]=='hstab_airfoil':
                    df = pd.read_csv(cd0_file)
                    match_row = df[df.iloc[:,0]== str(row[2])] #wing
                    self.hstab_cd0_prefactor = match_row.iloc[0,1]
                    self.hstab_cd0_expofactor = match_row.iloc[0,2]
                    self.hstab_airfoil = asb.Airfoil(row[2])
                elif row[0]=='vstab_airfoil':
                    df = pd.read_csv(cd0_file)
                    match_row = df[df.iloc[:,0]== str(row[2])] #wing
                    self.vstab_cd0_prefactor = match_row.iloc[0,1]
                    self.vstab_cd0_expofactor = match_row.iloc[0,2]
                    self.vstab_airfoil = asb.Airfoil(row[2])
    

    def _get_wing_volumes(self):
        def get_airfoil_area(airfoil):
            df = pd.read_csv(os.path.join(os.getcwd(),"airfoils", str(airfoil)+str('.dat')), sep='\s+', skiprows=1, header=None, names=['x', 'y'])
            df['x'] = df['x']
            df['y'] = df['y'] 
            coordinates = list(df.itertuples(index=False, name=None))
            cross_section_shape = shapely.Polygon(coordinates)
            cross_sectional_area= cross_section_shape.area
            return(float(cross_sectional_area))
        print(get_airfoil_area(self.airfoil),self.span)
        self.wing_volume = get_airfoil_area(self.airfoil) * self.span *self.chordlen
        self.tail_volume = get_airfoil_area(self.hstab_airfoil) * float(self.hstab_span) * float(self.hstab_chordlen)
        self.hstab_volume = get_airfoil_area(self.vstab_airfoil) * float(self.vstab_height) * float(self.vstab_chordlen)



plane = plane_values(csv_file)
print(vars(plane))

#Wing
wing_area = plane.span * plane.chordlen
wing_aspect_ratio = plane.span * plane.chordlen
wing_re = constants.density * plane.airspeed * plane.chordlen / constants.viscosity #Note 1

CL_wing = nf.get_aero_from_airfoil(
    airfoil=plane.airfoil,
    alpha=plane.wingaoa,
    Re = wing_re,
    model_size='xlarge'
)['CL'] #Note 2
wing_lift = CL_wing * 0.5 * constants.density * plane.airspeed**2 * wing_area #Note 3

wing_oswald = functions.oswald(wing_aspect_ratio) # Note 4
wing_CD_induced = CL_wing**2 / (constants.pi * wing_aspect_ratio * wing_oswald) 
wing_drag_induced = wing_CD_induced * 0.5 * constants.density * plane.airspeed**2 * wing_area #Note 5

wing_CD0 = plane.wing_cd0_prefactor * wing_re ** plane.wing_cd0_expofactor #Note 7
wing_drag_parasite = wing_CD0 * constants.density * plane.airspeed**2 * wing_area #Note 5

wing_foam_weight = plane.wing_volume * constants.foam_density * constants.g
wing_spar_weight = plane.span * constants.wingspar_linear_density * constants.g
wing_total_weight  = wing_foam_weight + wing_spar_weight

#Horizontal Stabilizer
hstab_area = plane.hstab_span * plane.hstab_chordlen
hstab_aspect_ratio = plane.hstab_span / plane.hstab_chordlen
hstab_re = constants.density * plane.airspeed * plane.hstab_chordlen / constants.viscosity

CL_hstab = nf.get_aero_from_airfoil(
    airfoil=plane.hstab_airfoil,
    alpha= -1 * float(plane.hstab_aoa), #Note 6
    Re = hstab_re,
    model_size='xlarge'
)['CL'] #Note 6
hstab_lift = -1 * CL_hstab * 0.5 * constants.density * plane.airspeed**2 * hstab_area #Note 6

hstab_oswald = functions.oswald(hstab_aspect_ratio) # Note 4
hstab_CD_induced = CL_hstab**2 / (constants.pi * hstab_aspect_ratio * hstab_oswald)
hstab_drag_induced = hstab_CD_induced * 0.5 * constants.density * plane.airspeed**2 * hstab_area # Note 5

hstab_CD0 = plane.hstab_cd0_prefactor * hstab_re ** plane.hstab_cd0_expofactor #Note 7
hstab_drag_parasite = hstab_CD0 * 0.5 * constants.density * plane.airspeed**2 * hstab_area

#Vertical Stabilizer
vstab_area = plane.vstab_height * plane.vstab_chordlen
vstab_re = constants.density * plane.airspeed * plane.vstab_chordlen / constants.viscosity

vstab_CD0 = plane.vstab_cd0_prefactor * vstab_re ** plane.hstab_cd0_expofactor
vstab_drag_parasite = vstab_CD0 * 0.5 * constants.density * plane.airspeed**2 * vstab_area #Note 8

#Fuselage 
fuselage_drag = plane.fuselage_cd * 0.5 * constants.density * plane.airspeed**2 * plane.fuselage_frontal_area

#Weight 
weight=plane.weight #Note 9

#Longitudional Static Stability
tail_volume_coeff = plane.LE_HstabLE_Dist * hstab_area / (plane.chordlen * wing_area)
static_margin = (plane.CG_LE_dist / plane.chordlen ) - 0.5 * tail_volume_coeff #Note 10

#Lift and Drag Totals
total_lift = wing_lift + hstab_lift 
total_drag = wing_drag_induced+wing_drag_parasite+hstab_drag_induced+hstab_drag_parasite+vstab_drag_parasite+fuselage_drag

#Power
power_in = plane.num_solar_cells * constants.solar_panel_size**2 * functions.get_solar_insolation(csv_file)
power_out = plane.airspeed * total_drag
power_ratio = power_in/power_out

#Constraints
opti.subject_to(total_lift==weight)

#Objective
opti.minimize(total_drag)
sol=opti.solve(max_iter=100)

for value in [
    "power_ratio",
    "hstab_CD_induced",
    "total_drag",
    "power_out",
    "plane.airspeed",
    "static_margin"
]:
    print(f"{value:10} = {sol(eval(value)):.6}")
