import pandas as pd

def remove_dat_from_csv(input_file, output_file):
    # Read CSV file
    df = pd.read_csv(input_file)
    
    # Remove '.dat' from the first column if present
    df.iloc[:, 0] = df.iloc[:, 0].str.replace(r'\.dat$', '', regex=True)
    
    # Save the updated CSV
    df.to_csv(output_file, index=False)

# Example usage
input_csv = 'airfoil_cd0.csv'  # Replace with your input file
output_csv = 'airfoil_cd0_nodat.csv'  # Replace with your desired output file
remove_dat_from_csv(input_csv, output_csv)
