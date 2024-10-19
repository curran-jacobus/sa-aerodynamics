import wing_area_optimization
import makeairfoilflat
import aircraft_parameters

import os


#Initialize Flat Airfoil
flatairfoilfile,flat_len_per_unit_chord = makeairfoilflat.make_flat_airfoil(aircraft_parameters.wing_airfoil_filename,aircraft_parameters.flat_after_percent_chord)
chord_step = aircraft_parameters.panel_size/flat_len_per_unit_chord
aircraft_parameters.wing_airfoil_filename=flatairfoilfile
aircraft_parameters.wing_airfoil_filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)),'airfoils',flatairfoilfile)

#optimize based on flat airfoil
wing_area_optimization.wing_hstab_area_optimization(chord_step)
