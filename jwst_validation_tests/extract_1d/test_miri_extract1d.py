#!/usr/bin/env python
# -*- coding:utf8 -*-

from astropy.io import fits
from jwst.extract_1d import Extract1dStep
from jwst import datamodels
import os
import numpy as np
#from shapely.geometry import Polygon
import math
from photutils import CircularAperture
from photutils import aperture_photometry

def test_mrs_spec2():
	""" 
	Test the extract1d step when reducing MRS data in spec2
	"""
	
	import tkinter as tk#  TKinter imported for a dialog box for choosing the file
	from tkinter import filedialog# TKinter also seems to be needed for matplotlib plots
	
	root = tk.Tk()
	root.withdraw()
	#read in cube from cube_build step that immediately precedes extract_1d step in Level 2b
	cubefile = "/Users/sargent/mirisim/20180813_123620_mirisim/det_images/det_image_seq1_MIRIFUSHORT_12SHORTexp1_s3d.fits"
	with fits.open(cubefile) as hduin:# open the cube file
		firstpart=cubefile[0:len(cubefile)-5]#a string with the part of the file path except the .fits extension
		tempfilepath=firstpart+'_temp.fits' # file name for temporary file
		fake_data= hduin['SCI'].data# read in cube
		print(fake_data.shape)
		fake_data[0:,0:,0:]=0.0# zero out all the pixels in the cube
		fake_data[0:,10,10]=100.0# add in a fake point source continuum in the zeroed-out cube
		fake_data[0:,10,9]=50.0# same
		fake_data[0:,9,10]=50.0# same
		fake_data[0:,11,10]=50.0# same
		fake_data[0:,10,11]=50.0# same

		fake_data[999,10,10]=150.0# add in fake point source emission line in zeroed-out cube
		fake_data[999,10,9]=75.0# same
		fake_data[999,9,10]=75.0# same
		fake_data[999,11,10]=75.0# same
		fake_data[999,10,11]=75.0# same
				
		fake_data[1000,10,10]=200.0# same
		fake_data[1000,10,9]=100.0# same
		fake_data[1000,9,10]=100.0# same
		fake_data[1000,11,10]=100.0# same
		fake_data[1000,10,11]=100.0# same
		
		fake_data[1001,10,10]=150.0# same
		fake_data[1001,10,9]=75.0# same
		fake_data[1001,9,10]=75.0# same
		fake_data[1001,11,10]=75.0# same
		fake_data[1001,10,11]=75.0# same
		hduin.writeto(tempfilepath,overwrite=True)# save the file with the fake signal in the cube
	
	apphotflux=np.zeros(fake_data.shape[0])
	for j in range(fake_data.shape[0]):# go through each slice of zeroed-out cube with fake signal
		position=[(10,10)]
		aperture=CircularAperture(position,r=3.)# perform aperture photometry on slice on fake signal
		phot_table=aperture_photometry(fake_data[j,:,:],aperture)
		apphotflux[j]=phot_table['aperture_sum']
	
	import matplotlib.pyplot as plt# this is needed to make plots
	
	#run the extract1d step
	result=Extract1dStep.call(tempfilepath,config_file="/Users/sargent/func/inst/nirspec/pipelinetesting/maria/configs72/extract_1d_mrs2.cfg")
	# perform extract_1d step on cube with fake signal
	outextractfile='/Users/sargent/mirisim/20180813_123620_mirisim/det_images/extract1dout_mrs2.fits'
	result.save(outextractfile)# save the result of the extract1d step
	with fits.open(outextractfile) as hdubackin:
		wl1d=hdubackin['EXTRACT1D'].data['wavelength']# read spectrum from extract1d step
		fl1d=hdubackin['EXTRACT1D'].data['flux']
		er1d=hdubackin['EXTRACT1D'].data['error']
		plt.plot(wl1d, fl1d, '.', color='r',markersize=4)# plot spectrum from extract1d step
		plt.plot(wl1d, apphotflux, '.', color='b',markersize=1)#overplot spectrum extracted 
		plt.xlabel('wavelength (microns)')# by doing aperture photometry on cube slices
		plt.ylabel('flux (Jy)')
		plt.title('Spectrum from Extract1d')
		plt.show()# show the spectrum
	
	relerror=(fl1d-apphotflux)/apphotflux# compute relative difference spectrum
	maxrelerr=max(relerror)# compute the maximum of the relative difference spectrum
	print("Maximum Relative Error for MRS Slit Level 2b")
	print(maxrelerr)
	plt.plot(wl1d, relerror, '-', color='r')# plot the relative difference spectrum
	plt.xlabel('wavelength (microns)')
	plt.ylabel('relative error (fraction)')
	plt.title('Relative Error for MRS Slit Level 2b')
	plt.show()

def test_lrs_slit_spec2():
	""" 
	Test the extract1d step when reducing LRS slit data in spec2
	"""

	import tkinter as tk#  TKinter imported for a dialog box for choosing the file
	from tkinter import filedialog# TKinter also seems to be needed for matplotlib plots
	
	root = tk.Tk()
	root.withdraw()
	# read in output from photom step, which immediately precedes the extract_1d step in Level 2b
	slitfile = "/Users/sargent/mirisim/20181004_131033_mirisim/det_images/photom1_photom.fits"
	with fits.open(slitfile) as hduslitin:
		hduslitin.info()
		slitim=hduslitin['SCI'].data
		relsens=hduslitin['RELSENS'].data# read in what should be the flux calibration spectrum
		wlrs=[i[0] for i in relsens]#to be able to reference a column in the relsens extension
		rsrs=[i[1] for i in relsens]#same
	
	#d is big array
	#l=[i[0] for i in d]
	
	dm_wcs = datamodels.open(slitfile)# read in WCS header information
	wcs = dm_wcs.meta.wcs
	
	extractwidth=41.# width of extraction window within bounding box of LRS Fixed Slit data
	lowerbb=wcs.bounding_box[0][0]
	upperbb=wcs.bounding_box[0][1]
	
	lotemp=((lowerbb+upperbb)/2.)-((extractwidth-1.)/2.)# x-coordinate of left side of extraction window
	hitemp=lotemp+(extractwidth-1.)# x-coordinate of right side of extraction window
	xstart=int(round(lotemp))#320#turn floats into integers
	xstop=int(round(hitemp))#342
	print(xstart)
	print(xstop)
	lopoly=float(xstart)-0.5
	hipoly=float(xstop)+0.5
	xcenter=(lopoly+hipoly)/2.# compute center of x-coordinate range of extraction window
	print("bounding box fixed slit")
	print(wcs.bounding_box[0])
	print(wcs.bounding_box[1])
	
	shape=(int(round(wcs.bounding_box[1][1]-wcs.bounding_box[1][0])),int(round(hitemp-lotemp))+1)
	grid=np.indices(shape, dtype=np.float64)# initialize indices for bounding box region
	grid[0] += round(wcs.bounding_box[1][0])# set indices for y-coordinates of bounding box
	grid[1] += xstart# set indices for x-coordinates of bounding box
	print(grid)
	tempwcswl=wcs(grid[1],grid[0])# compute wavelengths of pixels in bounding box using WCS
	wlgrid=tempwcswl[2]
	print(wlgrid)
	wlslitorig=wlgrid[:,20]# only want a vector of wavelengths, not a 2-d grid, when later plotting spectrum
	wlslit=wlslitorig[::-1]
	
	rsfactorback=np.interp(wlslitorig,wlrs[::-1],rsrs[::-1])# interpolate flux calibration spectrum to 
	rsfactor=rsfactorback[::-1]# LRS wavelength vector computed from WCS above
	
	rawflux=np.zeros(wlslitorig.shape[0])
	for j in range(wlslitorig.shape[0]):#add up the signal from each pixel in the extraction window on a row
		rawflux[j]=sum(slitim[j+int(round(wcs.bounding_box[1][0])),int(xstart):(int(xstop)+1)])#/(rsfactor[j])
	calflux=rawflux/rsfactorback# transform raw extracted spectrum to flux-calibrated spectrum
	
	import matplotlib.pyplot as plt# needed for making plots
	# fig1, ax1 = plt.subplots(figsize=(8, 8))
	# img1 = ax1.imshow(slitim, origin="lower", interpolation="none")
	# plt.show()
	
	#run the extract_1d step on the output of the photom step
	resultslit=Extract1dStep.call(slitfile,config_file="/Users/sargent/func/inst/nirspec/pipelinetesting/maria/configs72/extract_1d_slit2.cfg")
	outslitextractfile='/Users/sargent/func/inst/miri/pipelinetest/extract1d/extract1dslit2out.fits'
	resultslit.save(outslitextractfile)# write output spectrum of extract_1d step to file
	
	with fits.open(outslitextractfile, mode='update') as g:
		g.info()#read back in output spectrum from extract_1d step
		print(g['EXTRACT1D'])
		oute1d=g['EXTRACT1D'].data
		wle1d=[i[0] for i in oute1d]
		fluxe1d=[i[1] for i in oute1d]
		erre1d=[i[2] for i in oute1d]
	
	plt.plot(wle1d, fluxe1d)#plot the output spectrum from extract_1d step
	plt.plot(wlslitorig,rawflux,'-',color='r')#overplot result of performing row-by-row
	# extraction of signal from photom step output, for comparison
	plt.show()
	
	wlslittrim=wlslitorig[1:]# exclude first wavelength because it is NaN
	rawfluxtrim=rawflux[1:]
	
	fluxe1dint=np.interp(wlslittrim,wle1d[::-1],fluxe1d[::-1])# interpolate extract_1d step spectrum to WCS wavelength grid computed above
	relerror=(fluxe1dint-rawfluxtrim)/rawfluxtrim# determine relative difference between extract_1d spectrum and one computed row-by-row
	maxrelerr=max(relerror)# compute maximum relative difference
	print("Maximum Relative Error for LRS Slit Level 2b")
	print(maxrelerr)
	
def test_lrs_slitless_spec2():
	""" 
	Test the extract1d step when reducing LRS Slitless data in spec2
	"""

	import tkinter as tk# needed for matplotlib plotting
	from tkinter import filedialog
	
	root = tk.Tk()
	root.withdraw()
	slitlessfile="/Users/sargent/mirisim/20190114_212823_mirisim/det_images/stray/photom_photom.fits"
	with fits.open(slitlessfile) as hduslitlessin:# photom is last step before extract_1d in Level 2b for LRS Slitless data
		hduslitlessin.info()# so read in output from photom step
		slitlessim=hduslitlessin['SCI'].data
		relsens=hduslitlessin['RELSENS'].data
		wlrs=[i[0] for i in relsens]#to be able to reference a column in the relsens extension
		rsrs=[i[1] for i in relsens]#same
	
	#d is big array
	#l=[i[0] for i in d]
	
	dm_wcs = datamodels.open(slitfile)# read in WCS header information
	wcs = dm_wcs.meta.wcs
	
	extractwidth=41.# width of extraction window within bounding box of LRS Fixed Slit data
	lowerbb=wcs.bounding_box[0][0]
	upperbb=wcs.bounding_box[0][1]
	
	lotemp=((lowerbb+upperbb)/2.)-((extractwidth-1.)/2.)# x-coordinate of left side of extraction window
	hitemp=lotemp+(extractwidth-1.)# x-coordinate of right side of extraction window
	xstart=int(round(lotemp))#320#turn floats into integers
	xstop=int(round(hitemp))#342
	print(xstart)
	print(xstop)
	lopoly=float(xstart)-0.5
	hipoly=float(xstop)+0.5
	xcenter=(lopoly+hipoly)/2.# compute center of x-coordinate range of extraction window
	print("bounding box fixed slit")
	print(wcs.bounding_box[0])
	print(wcs.bounding_box[1])
	
	shape=(int(round(wcs.bounding_box[1][1]-wcs.bounding_box[1][0])),int(round(hitemp-lotemp))+1)
	grid=np.indices(shape, dtype=np.float64)# initialize indices for bounding box region
	grid[0] += round(wcs.bounding_box[1][0])# set indices for y-coordinates of bounding box
	grid[1] += xstart# set indices for x-coordinates of bounding box
	print(grid)
	tempwcswl=wcs(grid[1],grid[0])# compute wavelengths of pixels in bounding box using WCS
	wlgrid=tempwcswl[2]
	print(wlgrid)
	wlslitorig=wlgrid[:,20]# only want a vector of wavelengths, not a 2-d grid, when later plotting spectrum
	wlslit=wlslitorig[::-1]
	
	rsfactorback=np.interp(wlslitorig,wlrs[::-1],rsrs[::-1])# interpolate flux calibration spectrum to 
	rsfactor=rsfactorback[::-1]# LRS wavelength vector computed from WCS above
	
	rawflux=np.zeros(wlslitorig.shape[0])
	for j in range(wlslitorig.shape[0]):#add up the signal from each pixel in the extraction window on a row
		rawflux[j]=sum(slitim[j+int(round(wcs.bounding_box[1][0])),int(xstart):(int(xstop)+1)])#/(rsfactor[j])
	calflux=rawflux/rsfactorback# transform raw extracted spectrum to flux-calibrated spectrum
	
	import matplotlib.pyplot as plt# needed for making plots
	
	#plt.loglog(wlslitorig, rawflux)#rsfactorback)
	#plt.plot(wlslitorig, calflux, '-', color='r')
	##plt.xlabel('wavelength (microns)')
	##plt.ylabel('flux (Jy)')
	##plt.title('Spectrum from Extract1d')
	#plt.show()
	
	#run the extract_1d step on the output of the photom step
	resultslit=Extract1dStep.call(slitlessfile,config_file="/Users/sargent/func/inst/nirspec/pipelinetesting/maria/configs72/extract_1d_slitless2.cfg")
	outslitextractfile='/Users/sargent/func/inst/miri/pipelinetest/extract1d/extract1dslitless2out.fits'
	resultslit.save(outslitextractfile)# write output spectrum of extract_1d step to file
	
	with fits.open(outslitextractfile, mode='update') as g:
		g.info()#read back in output spectrum from extract_1d step
		print(g['EXTRACT1D'])
		oute1d=g['EXTRACT1D'].data
		wle1d=[i[0] for i in oute1d]
		fluxe1d=[i[1] for i in oute1d]
		erre1d=[i[2] for i in oute1d]
	
	wlslittrim=wlslitorig[1:]
	rawfluxtrim=rawflux[1:]
	
	plt.plot(wle1d, fluxe1d)#plot the output spectrum from extract_1d step
	plt.plot(wlslitorig,rawflux,'-',color='r')#overplot result of performing row-by-row
	# extraction of signal from photom step output, for comparison
	plt.show()
	
	wlslittrim=wlslitorig[1:]# exclude first wavelength because it is NaN
	rawfluxtrim=rawflux[1:]
	
	fluxe1dint=np.interp(wlslittrim,wle1d[::-1],fluxe1d[::-1])# interpolate extract_1d step spectrum to WCS wavelength grid computed above
	relerror=(fluxe1dint-rawfluxtrim)/rawfluxtrim# determine relative difference between extract_1d spectrum and one computed row-by-row
	maxrelerr=max(relerror)# compute maximum relative difference
	print("Maximum Relative Error for LRS Slitless Level 2b")
	print(maxrelerr)
	#plt.plot(wlslittrim, relerror, '-', color='r')# plot relative difference spectrum
	#plt.xlabel('wavelength (microns)')
	#plt.ylabel('relative error (fraction)')
	#plt.title('Relative Error for LRS Slitless Level 2b')
	#plt.show()

def test_mrs_spec3():
	""" 
	Test the extract1d step when reducing MRS data in spec3
	"""
	
	import tkinter as tk#  TKinter imported for a dialog box for choosing the file
	from tkinter import filedialog# TKinter also seems to be needed for matplotlib plots
	
	root = tk.Tk()
	root.withdraw()
	#read in cube from cube_build step that immediately precedes extract_1d step in Level 3
	cubefile = "/Users/sargent/mirisim/20180813_123620_mirisim/det_images/nod4point_ch1-short_s3d.fits"
	with fits.open(cubefile) as hduin:# open the cube file
		firstpart=cubefile[0:len(cubefile)-5]#a string with the part of the file path except the .fits extension
		tempfilepath=firstpart+'_temp.fits'# file name for temporary file
		fake_data= hduin['SCI'].data# read in cube
		print(fake_data.shape)
		fake_data[0:,0:,0:]=0.0# zero out all the pixels in the cube
		fake_data[0:,10,10]=100.0# add in a fake point source continuum in the zeroed-out cube
		fake_data[0:,10,9]=50.0# same
		fake_data[0:,9,10]=50.0# same
		fake_data[0:,11,10]=50.0# same
		fake_data[0:,10,11]=50.0# same

		fake_data[399,10,10]=150.0# add in fake point source emission line in zeroed-out cube
		fake_data[399,10,9]=75.0# same
		fake_data[399,9,10]=75.0# same
		fake_data[399,11,10]=75.0# same
		fake_data[399,10,11]=75.0# same
				
		fake_data[400,10,10]=200.0# same
		fake_data[400,10,9]=100.0# same
		fake_data[400,9,10]=100.0# same
		fake_data[400,11,10]=100.0# same
		fake_data[400,10,11]=100.0# same
		
		fake_data[401,10,10]=150.0# same
		fake_data[401,10,9]=75.0# same
		fake_data[401,9,10]=75.0# same
		fake_data[401,11,10]=75.0# same
		fake_data[401,10,11]=75.0# same
		hduin.writeto(tempfilepath,overwrite=True)# save the file with the fake signal in the cube
	
	apphotflux=np.zeros(fake_data.shape[0])
	for j in range(fake_data.shape[0]):# go through each slice of zeroed-out cube with fake signal
		position=[(10,10)]
		aperture=CircularAperture(position,r=3.)# perform aperture photometry on slice on fake signal
		phot_table=aperture_photometry(fake_data[j,:,:],aperture)
		apphotflux[j]=phot_table['aperture_sum']
	
	import matplotlib.pyplot as plt# this is needed to make plots
	
	#run the extract1d step
	result=Extract1dStep.call(tempfilepath,config_file="/Users/sargent/func/inst/nirspec/pipelinetesting/maria/configs72/extract_1d_mrs3.cfg")
	# perform extract_1d step on cube with fake signal
	outextractfile='/Users/sargent/mirisim/20180813_123620_mirisim/det_images/extract1dmrs3out.fits'
	result.save(outextractfile)# save the result of the extract1d step
	with fits.open(outextractfile) as hdubackin:
		wl1d=hdubackin['EXTRACT1D'].data['wavelength']# read spectrum from extract1d step
		fl1d=hdubackin['EXTRACT1D'].data['flux']
		er1d=hdubackin['EXTRACT1D'].data['error']
		plt.plot(wl1d, fl1d, '.', color='r',markersize=4)# plot spectrum from extract1d step
		plt.plot(wl1d, apphotflux, '.', color='b',markersize=1)#overplot spectrum extracted 
		plt.xlabel('wavelength (microns)')# by doing aperture photometry on cube slices
		plt.ylabel('flux (Jy)')
		plt.title('Spectrum from Extract1d')
		plt.show()# show the spectrum
	
	relerror=(fl1d-apphotflux)/apphotflux# compute relative difference spectrum
	maxrelerr=max(relerror)# compute the maximum of the relative difference spectrum
	print("Maximum Relative Error for MRS Slit Level 3")
	print(maxrelerr)
	plt.plot(wl1d, relerror, '-', color='r')# plot the relative difference spectrum
	plt.xlabel('wavelength (microns)')
	plt.ylabel('relative error (fraction)')
	plt.title('Relative Error for MRS Slit Level 3')
	plt.show()

def test_lrs_slit_spec3():
	""" 
	Test the extract1d step when reducing LRS slit data in spec3
	"""
	
	import tkinter as tk#  TKinter imported for a dialog box for choosing the file
	from tkinter import filedialog# TKinter also seems to be needed for matplotlib plots
	
	root = tk.Tk()
	root.withdraw()
	# read in output from photom step, which immediately precedes the extract_1d step in Level 2b
	slitfile = "/Users/sargent/mirisim/20181004_131033_mirisim/det_images/resample_level3_s2d.fits"
	with fits.open(slitfile) as hduslitin:
		hduslitin.info()
		slitim=hduslitin['SCI'].data
		relsens=hduslitin['RELSENS'].data# read in what should be the flux calibration spectrum
		wlrs=[i[0] for i in relsens]#to be able to reference a column in the relsens extension
		rsrs=[i[1] for i in relsens]#same
	
	#d is big array
	#l=[i[0] for i in d]
	
	dm_wcs = datamodels.open(slitfile)# read in WCS header information
	wcs = dm_wcs.meta.wcs
	
	extractwidth=41.# width of extraction window within bounding box of LRS Fixed Slit data
	lowerbb=wcs.bounding_box[0][0]
	upperbb=wcs.bounding_box[0][1]
	
	lotemp=((lowerbb+upperbb)/2.)-((extractwidth-1.)/2.)# x-coordinate of left side of extraction window
	hitemp=lotemp+(extractwidth-1.)# x-coordinate of right side of extraction window
	xstart=int(round(lotemp))#320#turn floats into integers
	xstop=int(round(hitemp))#342
	print(xstart)
	print(xstop)
	lopoly=float(xstart)-0.5
	hipoly=float(xstop)+0.5
	xcenter=(lopoly+hipoly)/2.# compute center of x-coordinate range of extraction window
	print("bounding box fixed slit")
	print(wcs.bounding_box[0])
	print(wcs.bounding_box[1])
	
	shape=(int(round(wcs.bounding_box[1][1]-wcs.bounding_box[1][0])),int(round(hitemp-lotemp))+1)
	grid=np.indices(shape, dtype=np.float64)# initialize indices for bounding box region
	grid[0] += round(wcs.bounding_box[1][0])# set indices for y-coordinates of bounding box
	grid[1] += xstart# set indices for x-coordinates of bounding box
	print(grid)
	tempwcswl=wcs(grid[1],grid[0])# compute wavelengths of pixels in bounding box using WCS
	wlgrid=tempwcswl[2]
	print(wlgrid)
	wlslitorig=wlgrid[:,20]# only want a vector of wavelengths, not a 2-d grid, when later plotting spectrum
	wlslit=wlslitorig[::-1]
	
	rsfactorback=np.interp(wlslitorig,wlrs[::-1],rsrs[::-1])# interpolate flux calibration spectrum to 
	rsfactor=rsfactorback[::-1]# LRS wavelength vector computed from WCS above
	
	rawflux=np.zeros(wlslitorig.shape[0])
	for j in range(wlslitorig.shape[0]):#add up the signal from each pixel in the extraction window on a row
		rawflux[j]=sum(slitim[j+int(round(wcs.bounding_box[1][0])),int(xstart):(int(xstop)+1)])#/(rsfactor[j])
	calflux=rawflux/rsfactorback# transform raw extracted spectrum to flux-calibrated spectrum
	
	import matplotlib.pyplot as plt# needed for making plots
	# fig1, ax1 = plt.subplots(figsize=(8, 8))
	# img1 = ax1.imshow(slitim, origin="lower", interpolation="none")
	# plt.show()
	
	#run the extract_1d step on the output of the photom step
	resultslit=Extract1dStep.call(slitfile,config_file="/Users/sargent/func/inst/nirspec/pipelinetesting/maria/configs72/extract_1d_slit3.cfg")
	outslitextractfile='/Users/sargent/func/inst/miri/pipelinetest/extract1d/extract1dslit3out.fits'
	resultslit.save(outslitextractfile)# write output spectrum of extract_1d step to file
	
	with fits.open(outslitextractfile, mode='update') as g:
		g.info()#read back in output spectrum from extract_1d step
		print(g['EXTRACT1D'])
		oute1d=g['EXTRACT1D'].data
		wle1d=[i[0] for i in oute1d]
		fluxe1d=[i[1] for i in oute1d]
		errore1d=[i[2] for i in oute1d]
		dqe1d=[i[3] for i in oute1d]
		nete1d=[i[4] for i in oute1d]
		nerrore1d=[i[5] for i in oute1d]
		backgrounde1d=[i[6] for i in oute1d]
		berrore1d=[i[7] for i in oute1d]
	
	plt.plot(wle1d, fluxe1d)#plot the output spectrum from extract_1d step
	plt.plot(wlslitorig,rawflux,'-',color='r')#overplot result of performing row-by-row
	# extraction of signal from photom step output, for comparison
	plt.show()
	
	wlslittrim=wlslitorig[1:]# exclude first wavelength because it is NaN
	rawfluxtrim=rawflux[1:]
	
	fluxe1dint=np.interp(wlslittrim,wle1d[::-1],fluxe1d[::-1])# interpolate extract_1d step spectrum to WCS wavelength grid computed above
	relerror=(fluxe1dint-rawfluxtrim)/rawfluxtrim# determine relative difference between extract_1d spectrum and one computed row-by-row
	maxrelerr=max(relerror)# compute maximum relative difference
	print("Maximum Relative Error for LRS Slit Level 3")
	print(maxrelerr)
	plt.plot(wlslittrim, relerror, '-', color='r')
	plt.xlabel('wavelength (microns)')
	plt.ylabel('relative error (fraction)')
	plt.title('Relative Error for LRS Slit Level 3')
	plt.show()

def test_lrs_slitless_spec3():
	""" 
	The Build 7.2 pipeline does not support this, so this will not be tested now.
	"""

if __name__ == '__main__':
	# test_mrs_spec2() # test extract_1d step for MRS data in Level 2b
	# test_lrs_slit_spec2() # test extract_1d step for LRS Fixed Slit data in Level 2b
	# test_lrs_slitless_spec2() # test extract_1d step for LRS Slitless data in Level 2b
	# test_mrs_spec3() # test extract_1d step for MRS data in Level 3
	test_lrs_slit_spec3() # test extract_1d step for LRS Fixed Slit data in Level 3
	# test_lrs_slitless_spec3() # test extract_1d step for LRS Slitless data in Level 3
