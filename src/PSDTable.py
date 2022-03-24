# PSD table model creation code
# AJY - January 2022
# Run this in Python 3

# We can use this to check to see if a file exists
import os.path
import sys

# HEASP has to be on the path - this is done by initialising HEASOFT first
from heasp import *

# Need to read FITS files to get "spectra"
from astropy.io import fits

# We need numpy for some arrays
import numpy as np

# Model name and energy band
# Soft
model_name = "PSDsoft"
band = "0p3-0p7keV"
# Hard
#model_name = "PSDhard"
#band = "0p7-1p5keV"

# Path to files containing the "spectra"
# Path for UOB computers
# path_to_files = "/data/typhon1/phajy/gx339-4/model-grid-gx339"
# Path for Docker on laptop (mount model grid to this folder)
path_to_files = "/research/model-grid-gx339"

# This is the grid size
# It starts off as negative which indicates it needs to be computed
n_e = -1			# needs to be computed
e_grid = []			# needs to be populated
e_bin_width = []	# needs to be populated

# model parameters
par_names = [
	"r_trc",		# truncation radius
	"r_sh",			# soft-hard transition radius
	"inc",			# inclination
	"disc_par",		# disc parameter (alpha*(H/R)^2)
	"emiss"			# emissivity
	]

# tabulated values
par_values = [
	[4, 6, 8, 13, 18, 23, 28, 35, 45, 55, 65, 75, 85, 95, 110, 120, 150], # r_trc
	[3, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100],	# r_sh
	[15, 30, 45, 60],	# inc
	[0.001, 0.005, 0.01, 0.05, 0.1],	# disc_par
	[0, 1, 2]	# emiss
	]

# Note that parameter combinations are only valid if t_trc > r_sh (i.e., truncation radius must be larger than soft-hard transition radius)

# initial values and delta
par_initial = [35.0, 15.0, 45.0, 0.01, 1]
par_delta = [2.5, 2.5, 5.0, 0.01, 0.1]

# Define reverberation table model
tab = table()

# set table descriptors and the energy array
tab.setModelName(model_name)
tab.setModelUnits(" ")
tab.setisRedshift(False)
tab.setisAdditive(True)
tab.setisError(False)

# all interpolated parameters
tab.setNumIntParams(len(par_names))
tab.setNumAddParams(0)
print("Number of parameters = %i" % len(par_names))

# add the list of parameters to table model
for i in range(len(par_names)):
	print( "par[%i] = %s with %i values" % (i, par_names[i], len(par_values[i])) )
	cur_par = tableParameter()
	cur_par.setName(par_names[i])
	cur_par.setInterpolationMethod(0)	# 0 - linear; 1 - logarithmic
	cur_par.setInitialValue(par_initial[i])
	cur_par.setDelta(par_delta[i])
	cur_par.setMinimum(par_values[i][0])
	cur_par.setBottom(par_values[i][0])
	cur_par.setTop(par_values[i][-1])
	cur_par.setMaximum(par_values[i][-1])
	cur_par_tab_vals = []
	for j in range(len(par_values[i])):
		cur_par_tab_vals.append(par_values[i][j])
	cur_par.setTabulatedValues(np.array(cur_par_tab_vals))

	# and push it onto the vector of parameters
	tab.pushParameter(cur_par)

# add spectra to table model
# calculate how many rows we'll have
# the first time we do this we will also add the energy grid
n_rows = 1
index = []
for i in range(len(par_names)):
	index.append(0)
	n_rows = n_rows * len(par_values[i])

print("Number of rows = %i" % n_rows)

for i in range(n_rows):
	# calculate indices
	k = i
	for j in range(len(par_names)):
		index[j] = k%len(par_values[j])
		k = k // len(par_values[j])
		# print("Parameter %s value %f (%i)" % (par_names[j], par_values[j][index[j]], index[j]))

	# Figure out the filename
	# Format is, e.g., psd-0p3-0p7keV-rtrc4-rsh3-dpar0p001-inc45-emss2.fits
	cur_file = "psd-" + band + "-rtrc{:d}-rsh{:d}-dpar0p{:03d}-inc{:2d}-emss{:d}.fits" . format(int(par_values[0][index[0]]), int(par_values[1][index[1]]), int(1000.0*par_values[3][index[3]]), int(par_values[2][index[2]]), int(par_values[4][index[4]]))

	print("File = %s" % cur_file)
	# input("  ...pause...")

	# clear current "spectrum" and add parameter values
	cur_spec = tableSpectrum()

	# make list of parameter values for the current "spectrum"
	cur_spec_par_vals = []
	for j in range(len(par_names)):
		cur_spec_par_vals.append(par_values[j][index[j]])
	cur_spec.setParameterValues(np.array(cur_spec_par_vals))

	# see if file exists (non-existent file might mean we have an invalid choice of parameters)
	if os.path.isfile(path_to_files + "/" + cur_file):
		# print("  file exists")
		hdulist = fits.open(path_to_files + "/" + cur_file)
		tabdata = hdulist[1].data

		# see if we need to read in the energy grid for the first time and set bin widths
		if (n_e < 0):
			n_e = len(tabdata)
			for j in range(n_e):
				e_grid.append(tabdata[j][0])
				tab.setEnergies(np.array(e_grid))
			for j in range(n_e-1):
				e_bin_width.append(e_grid[j+1]-e_grid[j])
			e_bin_width.append(e_bin_width[-1])	# repeat last value
			# input("  ...energy grid set...")

		# put the time lags into the table model
		cur_spec_flux = []
		# note that because we have bin hi and lo there are one fewer bins than there are energies
		for j in range(n_e-1):
			# table models contain quantities integrated over the bin width
			cur_spec_flux.append(tabdata[j][1] * e_bin_width[j])
		cur_spec.setFlux(np.array(cur_spec_flux))
	else:
		# print("  does not exist")
		# put zeros into the model if file does not exist (parameter choice is invalid) [check parameters are invalid]
		zero_flux = []
		for j in range(n_e-1):
			zero_flux.append(0.0)
		cur_spec.setFlux(np.array(zero_flux))
	tab.pushSpectrum(cur_spec)

# save table model
tab.write(model_name + ".mod")
