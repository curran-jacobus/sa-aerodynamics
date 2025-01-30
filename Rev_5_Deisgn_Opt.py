import csv
import numpy as np
import pandas as pd
import neuralfoil as nf
import aerosandbox as asb
import os

import core_functions.constants as constants

csv_file = os.path.join(os.getcwd(),'plane_csvs',"variable_loading_test.csv") #Update this per optimization

opti=asb.Opti()

#Import Aircraft-Dependent Paramters and Variables as Class Attribtutes
class plane_values:
    def __init__(self, csv_file):
        self._load_params(csv_file)
        self._load_opti_vars(csv_file)
        self._get_CD0()

    def _load_params(self, csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                name, type, value, min, max = row
                if type == 'p':
                    setattr(self, name.strip(), value)

    def _load_opti_vars(self, csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                name, type, value, min, max = row
                if type == 'v':
                    setattr(self, name.strip(), opti.variable(init_guess=float(value), lower_bound=float(min), upper_bound= float(max)))

    def _get_CD0(self, cd0_file = "airfoil_cd0.csv"):
        df = pd.read_csv(cd0_file)
        match_row = df[df.iloc[:,0]== self.airfoil]
        self.cd0_prefactor = match_row.iloc[0,1]
        self.cd0_expofactor = match_row.iloc[0,2]

plane = plane_values(csv_file) #update CSV File Here

