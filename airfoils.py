import neuralfoil as nf
import numpy as np
import pandas as pd

def lin_interpolate_CD0(df):
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

def get_CD0_Cl_Cd(airfoil_filepath, reynolds):
    aero_data=pd.DataFrame({"Alpha": [], 'CL': [], 'CD': []})
    for aoa in np.linspace(-15,15,301):
        data_alpha = nf.get_aero_from_dat_file(
            filename=airfoil_filepath,
            alpha=aoa,
            Re = reynolds,
            model_size='xlarge')
        aero_data_row = pd.DataFrame({"Alpha": [aoa], 'CL': [data_alpha["CL"]], 'CD': [data_alpha["CD"]]})
        aero_data=pd.concat([aero_data,aero_data_row])

    CD0 = lin_interpolate_CD0(aero_data)
    CL = aero_data[aero_data['Alpha'] == 0]['CL'].values[0]
    CD = aero_data[aero_data['Alpha'] == 0]['CD'].values[0]
    return {"CD0": CD0, "CL": CL, "CD":CD}