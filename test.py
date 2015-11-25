#import settings
#from pyvislc.utils import phase_fold
import numpy as np
from fast_labeler import Labeler
#import utils.readhatlc as rhlc
import os, sys, gzip
#import utils.miscutils as mutils
import matplotlib.pyplot as plt
#import utils.featureutils as futils
import cPickle as pickle
#import argparse
from math import *



key_mapping = {
		 'q' : 'RRab', 'w' : 'RRab-RRc', 'e' : 'RRc', 'r' : 'Variable-not-RR', 't' : 'Unsure' , 'y' : 'Not-variable', 'p' : 'Problem'
	}

fig_folder = '/Users/jah5/Documents/Fall2014_Gaspar/rrlyr_classification/plots'
pf_fig_name = lambda hatid : '%s/%s_pf.png'%(fig_folder, hatid)

hatids = pickle.load(open('/Users/jah5/Documents/Fall2014_Gaspar/rrlyr_classification/SCRATCH/candidates/candidates_rrab_v4_iter0006/candidate_ids.pkl', 'rb'))
hatids = [ hatid for hatid in hatids if os.path.exists(pf_fig_name(hatid))]

image_files = { hatid : [ pf_fig_name(hatid) ] for hatid in hatids }
label_file = 'fast_labeling_results.dat'

# Now label away!!
labeler = Labeler(image_files, label_file, sorted(key_mapping.values()), key_mapping)
labeler.connect()
plt.show(block=True)

'''
def fast_ax_candidate_pf(ax,hatid,lc_fname, ft_fname, show_fit=True, phase=0.0):
	""" Adds a phase-folded plot to a matplotlib.Axis instance

	    inputs:
	        ax          matplotlib.Axis instance to which phase-folded plot will be added
	        t           Central values of phase bins
	        y           Average magnitude in each phase bin
	        opts        Options (required, should contain 'ylabel', 'period', 'yerr' )

	"""
	
	# Open lightcurve and get features.
	#lc_fname = candidate_filenames[candidate_ids.index(hatid)]
	if not os.path.exists(lc_fname):
		ax.text(0.5, 0.5, '%s not found'%(lc_fname), transform=ax.transAxes, ha='center')
		return False
	else:
		lc = pickle.load(gzip.open(lc_fname, 'rb'))
		if lc is None:
			ax.text(0.5, 0.5, 'Lightcurve is None'%(lc_fname), transform=ax.transAxes, ha='center')
			return False
	# Raw time/mags
	ytype = 'TF2'
	t_, y_ = lc['BJD'], lc[ytype]
	try:
		t_ = [ float(T) for T in t_ ]
		y_ = [ float(Y) for Y in y_ ]
	except ValueError:
		print "Warning: %s cannot convert t, y"%(hatid)
		return False
		
	# Get features/period
	features = pickle.load(open(ft_fname, 'rb'))
	period = features['p1']

	# Phase fold
	t, y, junk = phase_fold(t_, y_, period)

	# edit that to get 0, 2 phase
	inds = np.arange(len(t))
	np.random.shuffle(inds)
	add_ones = inds[:len(inds)/2]
	T2 = [ T + 1. if i in add_ones else T for i,T in enumerate(t)  ]
	
	# Scatter plot
	ax.scatter(T2 , y, label="P=%.4f days"%(period),c='b',alpha=0.05, marker=',')

	# Get info about the fit
	amplitudes, phases, C = mutils.translate_features_to_fit_params(features)

	fitfunc = lambda T : C + sum( [ A * cos(2*np.pi*N*T - PHI) for A,N,PHI in zip(amplitudes, np.arange(1, len(amplitudes) + 1) , phases) ] )

	if show_fit:
		tfit = np.linspace(0, 2)
		yfit = np.array( [ fitfunc( T - phase ) for T in tfit ])
		ax.plot( tfit, yfit, lw=2, color='r')

	ax.set_ylabel(ytype)
	ax.set_xlabel("Phase")
	ax.set_title("Phase-folded")
	ax.text(0.05, 0.95, '%s'%(hatid), transform=ax.transAxes, ha='left', va='top')
	ax.set_xlim(0,2)
	ax.legend(loc='upper right', fontsize=9)
	ax.invert_yaxis()
	

	ax.format_coord = lambda x, y : ''
	return True
'''
