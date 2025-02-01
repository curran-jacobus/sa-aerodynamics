import csv
import numpy as np
import pandas as pd
import neuralfoil as nf
import aerosandbox as asb
import os
import re

#import core_functions.constants as constants
#import core_functions.functions as functions

csv_file = os.path.join(os.getcwd(),'plane_csvs',"variable_loading_test.csv") #Update this per optimization

opti=asb.Opti()

#Import Aircraft-Dependent Paramters and Variables as Class Attribtutes
class plane_values:
    def __init__(self, csv_file):
        #self._load_params(csv_file)
        self._load_opti_vars(csv_file)
        #self._construct_airfoil_objects(csv_file)
        #self._get_CD0() #This may not be needed with VLM parameter
    
    #ensure airfoil is from this list
    #https://github.com/peterdsharpe/AeroSandbox/tree/master/aerosandbox/geometry/airfoil/airfoil_database
    
    def _load_params(self, csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                name, type, value, min, max = row
                
    
    def _load_opti_vars(self, csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                name, type, value, min, max = row
                if type == 'v':
                    if name=='ï»¿span':
                        setattr(self, re.sub(r'[^a-zA-Z_]+', '', name.strip()),opti.variable(init_guess=float(value), lower_bound=float(min), upper_bound= float(max)))
                    else:
                        setattr(self, name.strip(),opti.variable(init_guess=float(value), lower_bound=float(min), upper_bound= float(max)))
                elif type == 'p':
                    if name=="ï»¿span":
                        setattr(self, re.sub(r'[^a-zA-Z_]+', '', name.strip()),float(value))
                    
                    elif re.search(r'airfoil',name):
                        print(name)
                        setattr(self,name,asb.Airfoil("naca2412")) #THIS NEEDS TO BE FIXED FOR NON-NACA Airfoils
                    else:
                        setattr(self, name.strip(),float(value))

    def _get_CD0(self, cd0_file = "airfoil_cd0.csv"):
        df = pd.read_csv(cd0_file)
        match_row = df[df.iloc[:,0]== self.airfoil]
        self.cd0_prefactor = match_row.iloc[0,1]
        self.cd0_expofactor = match_row.iloc[0,2]
    
    def _construct_airfoil_objects(self,csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                name, type, value, min, max = row
                if re.search(r'airfoil',name):
                    print(name)
                    setattr(self,name,asb.Airfoil(name))

plane = plane_values(csv_file)
print(vars(plane))

#Vortex Lattice Method - ADD FUSELAGE
vlm_airplane =  asb.Airplane(
    xyz_ref=[-1 * plane.CG_LE_dist,0,0], #Move the CG Forward of the Reference (CG)
    wings=[
        
        asb.Wing(
            name="Horizontal Stabilizer",
            symmetric = True,
            x_le = plane.LE_HstabLE_Dist,
            xsecs=[
                asb.WingXSec( #Root
                    xyz_le = [0,0,0],
                    airfoil = plane.hstab_airfoil,
                    twist=plane.hstab_aoa,
                    chord = plane.hstab_chordlen
                ),
                asb.WingXSec( #Tip
                    xyz_le = [0,plane.hstab_span/2,0],
                    airfoil = plane.hstab_airfoil,
                    twist=plane.hstab_aoa,
                    chord = plane.hstab_chordlen
                )
            ]
        ),

        asb.Wing(
            name="Main Wing",
            symmetric = True,
            x_le = 0, # Everything is referenced to the LE, as per the spreadsheet
            xsecs=[
                asb.WingXSec( # Root
                    xyz_le=[0,0,0], #LE position to LE Leave 0
                    airfoil = plane.airfoil,
                    twist = plane.wing_aoa,
                    chord = plane.chordlen
                ),
                asb.WingXSec( # Tip
                    xyz_le=[0,plane.span/2,0],
                    airfoil = plane.airfoil,
                    twist = plane.wing_aoa,
                    chord = plane.chordlen
                )
            ]
        ),



        asb.Wing(
            name="Vertical Stabilizer",
            symmetric = True,
            x_le = plane.LE_VstabLE_Dist,
            xsecs=[
                asb.WingXSec( #Bottom
                    xyz_le = [0,0,0],
                    airfoil = plane.vstab_airfoil,
                    chord = plane.vstab_chordlen,
                    twist = 0
                ),
                asb.WingXSec( #Top
                    xyz_le = [0,0,plane.vstab_height],
                    airfoil = plane.vstab_airfoil,
                    chord = plane.vstab_chordlen,
                    twist = 0
                )
            ]
        )


    ]
)

vlm=asb.VortexLatticeMethod(
    airplane= vlm_airplane,
    op_point= asb.OperatingPoint(
        velocity=plane.airspeed,
            )
)
aero = vlm.run()


L_over_D = aero["L"]/aero["D"]
#Constrtaints:
#opti.subject_to(plane.LE_VstabLE_Dist == plane.LE_HstabLE_Dist + plane.HstabLE_VstabLE_offset)

opti.maximize(L_over_D)

sol = opti.solve(max_iter=500)
print(sol(eval("L_over_D")))