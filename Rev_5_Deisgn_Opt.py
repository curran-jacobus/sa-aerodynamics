import csv
import numpy as np
import pandas as pd
import neuralfoil as nf
import aerosandbox as asb
import os

import core_functions.constants as constants


opti=asb.Opti()
class plane_values:
    def __init__(self, csv_file):
        self._load_params(csv_file)
        self._load_opti_vars(csv_file)
        #self._calc_CD0_regression()

    def _load_params(self, csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                name, type, value, min, max = row
                if type == 'p':
                    setattr(self, name.strip(), float(value.strip()))

    def _load_opti_vars(self, csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                name, type, value, min, max = row
                if type == 'v':
                    setattr(self, name.strip(), opti.variable(init_guess=float(value), lower_bound=float(min), upper_bound= float(max)))

    def _calc_CD0_regression(self, re_list=np.linspace(1e5,1e6,10)):
        def fit_power_law(x, y):
            #power law was found to fit CD0 vs Re regressions very well r^2 >0.99 for 5 airfoils. Curran Jacobus 12/1/2024
            if len(x) != len(y):
                raise ValueError("x and y must have the same length.")
            
            # Convert to numpy arrays for easier manipulation
            x = np.array(x)
            y = np.array(y)
            
            if np.any(x <= 0) or np.any(y <= 0):
                raise ValueError("All x and y values must be positive for logarithmic fitting.")
            
            # Take the logarithm of x and y
            log_x = np.log(x)
            log_y = np.log(y)
            
            # Perform linear regression in log-log space
            A = np.vstack([log_x, np.ones_like(log_x)]).T
            coeffs, _, _, _ = np.linalg.lstsq(A, log_y, rcond=None)
            
            # Extract the coefficients
            expo_factor = coeffs[0]
            log_prefactor = coeffs[1]
            prefactor = np.exp(log_prefactor)
            
            return float(prefactor), float(expo_factor)

        def lin_interpolate_CD0(df):
            #Linear Interpolates Coefficient of Drag for when Coefficient of Lift is 0 (CD0)

            # Sort by CL in ascending order to ensure proper interpolation
            df = df.sort_values(by='CL').reset_index(drop=True)

            # Find the indices of the CL values just below and above 0
            cl_below = df[df['CL'] < 0].iloc[-1]  # Last value where CL < 0
            cl_above = df[df['CL'] > 0].iloc[0]   # First value where CL > 0

            # Extract the CL and CD values for interpolation
            cl1, cd1 = cl_below['CL'], cl_below['CD']
            cl2, cd2 = cl_above['CL'], cl_above['CD']

            # Perform linear interpolation for CD when CL = 0
            cd_at_cl_zero = cd1 + (0 - cl1) * (cd2 - cd1) / (cl2 - cl1)

            return cd_at_cl_zero

        def get_CD0(reynolds,airfoil_filepath):
            #Returns three key airfoil parameters in a dictionary

            #Calculate aerodynamic parameters over range of AoA values, saves to dataframe
            aero_data=pd.DataFrame({"Alpha": [], 'CL': [], 'CD': []})
            for aoa in np.arange(-15,15,0.5):
                data_alpha = nf.get_aero_from_dat_file(
                    filename=airfoil_filepath,
                    alpha=aoa,
                    Re = reynolds,
                    model_size='xlarge')
                aero_data_row = pd.DataFrame({"Alpha": [aoa], 'CL': [data_alpha["CL"]], 'CD': [data_alpha["CD"]]})
                aero_data=pd.concat([aero_data,aero_data_row])
            #Desired Values Extracted from Data Frame
            CD0 = lin_interpolate_CD0(aero_data)
            return CD0
        
        cd0_list=[]
        for re in re_list:
            cd0_list.append(get_CD0(re,self.airfoilfile))
        
        prefactor,expofactor = fit_power_law(re_list,cd0_list)
        self.cd0_prefactor =  prefactor
        self.cd0_expofactor = expofactor
        
p = plane_values(os.path.join(os.getcwd(),'plane_csvs',"variable_loading_test.csv")) #update CSV File Here

