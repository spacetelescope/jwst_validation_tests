#!/usr/bin/env python
# -*- coding:utf8 -*-

from astropy.io import fits
from jwst.straylight import StraylightStep
import numpy as np
import math

def test_stray():
	"""
	Test the stray step when reducing MRS slit data in spec2
	"""
	# The srctype step is the step immediately preceding the stray_light step in calwebb_spec2.cfg, so to isolate the
	#	effects of the stray_light step, the output of the srctype step should be the input of the stray_light step.
	#	The data processed by the pipeline up to the stray_light step is from mirisim, which does not include stray 
	#	light.  This makes for a good data set to use in testing, so that exactly the stray light component added 
	#	should be the amount that is removed by the stray_light step, if the stray_light step works correctly.
	srctypefile = "/Users/sargent/mirisim/20180813_123620_mirisim/det_images/straytest2019/srctype_srctype.fits"
	
	srctypedata=fits.getdata(srctypefile,'SCI')#this reads in the srctype data
	
	sigmax=(100.)/(2.*((2.*(math.log(2.)))**(0.5)))
	sigmay=(400.)/(2.*((2.*(math.log(2.)))**(0.5)))
	g2d=np.zeros((srctypedata.shape[0],srctypedata.shape[1]))# create an array the size of the srctype data 
	for i in range(srctypedata.shape[1]):#to hold the fake stray light signal
		for j in range(srctypedata.shape[0]):
			g2d[j,i]=(1.35)*(math.exp((-0.5)*((((i-(332.))/sigmax)**(2.))+(((j-(511.))/sigmay)**(2.)))))
			# the fake signal is a 2-dimensional gaussian with an elliptical footprint
	
	fakefile="/Users/sargent/mirisim/20180813_123620_mirisim/det_images/straytest2019/onlyfake.fits"
	hduonlyfake=fits.PrimaryHDU(g2d)
	hduonlyfake.writeto(fakefile,overwrite=True)# write out the array with fake signal to file
	
	srctypeplusg2d=srctypedata+g2d # add the fake stray light signal to the (stray-light-less) srctype data
	
	hdul=fits.open(srctypefile,mode='update')
	
	file2="/Users/sargent/mirisim/20180813_123620_mirisim/det_images/straytest2019/srctype_plus_fake.fits"
	hdul.writeto(file2,overwrite=True)# write a file that will hold the srctype plus fake signal data
	
	with fits.open(file2, 'update') as f:
		f[1].data=srctypeplusg2d# update srctype plus fake signal file to hold actual srctype plus fake signal data
	
	result=StraylightStep.call(file2)# stray_light step works on srctype output plus fake signal
	result.save('/Users/sargent/mirisim/20180813_123620_mirisim/det_images/straytest2019/simplusfakeminusfake.fits')
	# save output from stray_light step, which has stray light removed by the stray_light step
	
	with fits.open('/Users/sargent/mirisim/20180813_123620_mirisim/det_images/straytest2019/simplusfakeminusfake.fits', mode='update') as g:
		strayfromstep=srctypeplusg2d-g[1].data # read back in the output from the stray_light step (which had stray light removed)
		# and then subtract that from the file that was srctype plus the fake signal.  The difference should be what 
		# was removed by the stray_light step
	
	outfile='/Users/sargent/mirisim/20180813_123620_mirisim/det_images/straytest2019/subtracted_fake_signal.fits'
	hduout=fits.PrimaryHDU(strayfromstep)
	hduout.writeto(outfile,overwrite=True)# write out to file the component of signal that was removed by the stray_light step
	
	# compute an image of the relative difference between component removed by stray_light step
	reldiff=(g2d-strayfromstep)/g2d# and the fake signal that was added to the srctype step output
	vertcut=reldiff[:,332]#make a line cut through the relative difference image
	cutind=np.zeros(vertcut.shape[0])
	for i in range(vertcut.shape[0]):
		cutind[i]=i
	maxrelerr=max(vertcut)
	print("Maximum relative error at the column (index 332, the 333rd) of maximum injected signal is")
	print(maxrelerr)
	
	residfile='/Users/sargent/mirisim/20180813_123620_mirisim/det_images/straytest2019/reldiff.fits'
	hdures=fits.PrimaryHDU(reldiff)
	hdures.writeto(residfile,overwrite=True)# write out the relative difference image
	
	import tkinter as tk#  TKinter imported for a dialog box for choosing the file (if desired)
	from tkinter import filedialog#  
	
	root = tk.Tk()
	root.withdraw()# TKinter also seems to be needed for matplotlib plots
	
	import matplotlib.pyplot as plt
	plt.plot(cutind, vertcut, '-', color='r')# plot a vertical line cut of the relative difference image
	plt.plot(cutind, vertcut)#, '-', color='r')
	plt.xlabel('y position')
	plt.ylabel('relative error (fraction)')
	plt.title('Relative Error for vertical line cut at maximum signal')
	plt.show()

if __name__ == '__main__':
	test_stray()
