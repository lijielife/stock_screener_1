#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib2
import csv
import sys
import string
from dateutil import parser as date_parser
from datetime import timedelta
from datetime import date
from datetime import datetime
import numpy as np
from itertools import islice
import time
import os

class Data():

    def __init__(self, stock, time_period):
	#Today's date:
	today = date.today()
	print stock
	#Load End of Day Quote from Google, then store in a temporary file
	if time_period == '1 day':
		eod_quote = urllib2.urlopen("https://www.google.com/finance/getprices?i=%i&p=%id&f=d,o,h,l,c,v&df=cpct&q=%s" %
			(60, 1, string.upper(stock)))
	if time_period == '2 days':
		eod_quote = urllib2.urlopen("https://www.google.com/finance/getprices?i=%i&p=%id&f=d,o,h,l,c,v&df=cpct&q=%s" %
			(120, 2, string.upper(stock)))
	if time_period == '1 week':
		eod_quote = urllib2.urlopen("https://www.google.com/finance/getprices?i=%i&p=%id&f=d,o,h,l,c,v&df=cpct&q=%s" %
			(600, 5, string.upper(stock)))
		print "https://www.google.com/finance/getprices?i=%i&p=%id&f=d,o,h,l,c,v&df=cpct&q=%s" %(360, 5, string.upper(stock))
	if time_period == '1 month':
		eod_quote = urllib2.urlopen("https://www.google.com/finance/getprices?i=%i&p=%id&f=d,o,h,l,c,v&df=cpct&q=%s" %
			(360, 30, string.upper(stock)))
	if time_period == '1 year':
		eod_quote = urllib2.urlopen("http://ichart.finance.yahoo.com/table.csv?s=%s&a=%i&b=%i&c=%i&d=%i&e=%i&f=%i&g=d&ignore=.csv" %
			(string.upper(stock),today.month, today.day, today.year-1, today.month, today.day, today.year ))
		print "http://ichart.finance.yahoo.com/table.csv?s=%s&a=%i&b=%i&c=%i&d=%i&e=%i&f=%i&g=d&ignore=.csv" %(string.upper(stock),today.month, today.day, today.year-1, today.month, today.day, today.year )
	if time_period == '5 years':
		eod_quote = urllib2.urlopen("http://ichart.finance.yahoo.com/table.csv?s=%s&a=%i&b=%i&c=%i&d=%i&e=%i&f=%i&g=d&ignore=.csv" %
			(string.upper(stock),today.month, today.day, today.year-5, today.month, today.day, today.year ))

	#Get Company Info
	company_info = urllib2.urlopen("http://finance.yahoo.com/d/quotes.csv?s=%s&f=sob2b3a2c6ee8ghjkj1p5p6rt8xk1t1d1nk2pdys" %
			(string.upper(stock)))

	#time.sleep(0.5)
	output = open('./eod_quotes/'+stock+'.dat', 'w')
	output.write(eod_quote.read())
	output.close()
	output_company_info = open('./company_info/'+stock+'.dat', 'w')
	output_company_info.write(company_info.read())
	output_company_info.close()

	#Parse the temporary file
	self.date_stamp = []
	self.open_val = []
	self.close_val = []
	self.low_val = []
	self.high_val = []
	self.volume_val = []

	self.date = []


	#If using googles API:
	if time_period in ['1 day', '2 days', '1 week', '1 month']:
		with open('./eod_quotes/'+stock+'.dat', 'r') as csvfile:
			eod_reader = csv.reader(csvfile, delimiter = ',')
			row_num = 0
			for row in eod_reader:

				#Some shitty programming to get intervals and timestamps from the google data header
				if row_num < 8:
					if row_num == 3:
						self.interval = row[0]
						self.interval = int(self.interval[9:])
					if row_num == 7:
						self.benchmark = int(row[0][1:]) + 10800	#time difference btw east and west coasts
				else:
					self.date_stamp.append(row[0])
					self.open_val.append(row[4])
					self.high_val.append(row[2])
					self.low_val.append(row[3])
					self.close_val.append(row[1])
					self.volume_val.append(row[5])
				row_num = row_num +1

		#Dealing with google's ridiculous way of writing datestamps
		for i in range(len(self.date_stamp)):
			if self.date_stamp[i][0] =='a':
				self.benchmark = int(self.date_stamp[i][1:]) + 10800
				self.date_stamp[i] = int(self.date_stamp[i][1:]) + 10800
			else:
				self.date_stamp[i] = int(self.date_stamp[i])*self.interval+self.benchmark
		#Format date strings to something matplotlib can work with
		for item in self.date_stamp:
			self.date.append(datetime.fromtimestamp(item))

	#If using Yahoo's API:
	elif time_period in ['1 year', '5 years']:
		row_num = 0
		with open('./eod_quotes/'+stock+'.dat', 'r') as csvfile:
			eod_reader = csv.reader(csvfile, delimiter = ',')
			for row in eod_reader:
				if row_num == 0:
					pass
				else:
					self.date_stamp.append(row[0])
					self.open_val.append(row[1])
					self.high_val.append(row[2])
					self.low_val.append(row[3])
					self.close_val.append(row[4])
					self.volume_val.append(row[5])
				row_num = row_num + 1

		#Reverse all lists
		self.date_stamp = self.date_stamp[::-1]
		self.open_val = self.open_val[::-1]
		self.high_val = self.high_val[::-1]
		self.low_val = self.low_val[::-1]
		self.close_val = self.close_val[::-1]
		self.volume_val = self.volume_val[::-1]
		#Parse datestamps into datetime objects
		for item in self.date_stamp:
			self.date.append(date_parser.parse(item))


	for i in range(len(self.open_val)):
		self.open_val[i] = float(self.open_val[i])
		self.close_val[i] = float(self.close_val[i])
		self.high_val[i] = float(self.high_val[i])
		self.low_val[i] = float(self.low_val[i])
		self.volume_val[i] = float(self.volume_val[i])


	#Make numpy arrays of the data, in case you want to do any calculations with it
	self.open_val_array = np.array(self.open_val)
	self.close_val_array = np.array(self.close_val)
	self.high_val_array = np.array(self.high_val)
	self.low_val_array = np.array(self.low_val)
	self.volume_val_array = np.array(self.volume_val)



	#Normalized Volumes for plotting
	for i in range(len(self.volume_val)):
		#self.volume_val[i] = self.volume_val[i]/max(self.volume_val)
		pass

	#Fourier Filter data
	def smooth(self, x,window_len,window='hanning'):
		'''if x.ndim != 1:
		        raise ValueError, "smooth only accepts 1 dimension arrays."
		if x.size < window_len:
		        raise ValueError, "Input vector needs to be bigger than window size."
		if window_len<3:
		        return x
		'''
		if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
		        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
		s=np.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
		if window == 'flat': #moving average
		        w=np.ones(window_len,'d')
		else:  
		        w=eval('np.'+window+'(window_len)')
		y=np.convolve(w/w.sum(),s,mode='same')
		return y[window_len:-window_len+1]


	#Moving averages

	def window(seq, n=2):
	    "Returns a sliding window (of width n) over data from the iterable"
	    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
	    it = iter(seq)
	    result = tuple(islice(it, n))
	    if len(result) == n:
		yield result    
	    for elem in it:
		result = result[1:] + (elem,)
		yield result
	def moving_averages(values, size):
	    for _ in range(size - 1):
		yield 0
	    for selection in window(values, size):
		yield sum(selection) / size

	#Bollinger Bands

	def upper_bollinger(values, size):
	    for _ in range(size - 1):
		yield 0
	    for selection in window(values, size):
		yield sum(selection) / size + 2*np.std(selection)
	def lower_bollinger(values, size):
	    for _ in range(size - 1):
		yield 0
	    for selection in window(values, size):
		yield sum(selection) / size - 2*np.std(selection)


	try:
		#Calcualte all the quantities for the GUI
		self.close_5day = []
		for avg in moving_averages(self.close_val, 5):
			self.close_5day.append(avg)
		self.close_21day = []
		for avg in moving_averages(self.close_val, 21):
			self.close_21day.append(avg)
		self.close_20day = []
		for avg in moving_averages(self.close_val, 20):
			self.close_20day.append(avg)
		self.upper_bollinger_band = []
		for avg in upper_bollinger(self.close_val, 20):
			self.upper_bollinger_band.append(avg)
		self.lower_bollinger_band = []
		for avg in lower_bollinger(self.close_val, 20):
			self.lower_bollinger_band.append(avg)
		self.smoothed_close = smooth(self, self.close_val_array, 21)

	except IndexError:
		print 'not enough data yet'
	self.derivative_close = np.gradient(self.smoothed_close) / self.smoothed_close			#Normalized derivative
	self.second_derivative_close = np.gradient(self.derivative_close) / self.smoothed_close		#Normalized derivative


	#Parse the company information
	company_info_array = []
	with open('./company_info/'+stock+'.dat', 'r') as csvfile:
			company_info_reader = csv.reader(csvfile, delimiter = ',')
			for row in company_info_reader:
				if row[0] != row[26]:
					error_msg = "Yahoo produced badly formatted data for this stock.  Data not available at this time."
					break
				else:
					for val in row:
						if val == 'N/A':
							company_info_array.append('0')
						else:
							company_info_array.append(val)

			self.sym = company_info_array[0]
			self.open_val = company_info_array[1]
			self.ask = company_info_array[2]
			self.bid = company_info_array[3]
			self.avg_daily_vol = company_info_array[4]
			self.change = company_info_array[5]
			self.eps = company_info_array[6]
			self.eps_est_next_yr = company_info_array[7]
			self.day_low = company_info_array[8]
			self.day_high = company_info_array[9]
			self.fiftytwo_week_low = company_info_array[10]
			self.fiftytwo_week_high = company_info_array[11]
			self.mkt_cap = company_info_array[12]
			self.ps = company_info_array[13]
			self.pb = company_info_array[14]
			self.pe = company_info_array[15]
			self.target_1yr = company_info_array[16]
			self.exchange = company_info_array[17]
			self.price = company_info_array[18]
			self.trade_time = company_info_array[19]
			self.trade_date = company_info_array[20]
			self.name = company_info_array[21]
			self.prev_close = company_info_array[23]
			self.dividend = company_info_array[24]
			self.dividend_yield = company_info_array[25]
			try:
				self.change_percent = str(float(self.change)/float(self.prev_close)*100)[:5]+'%'
			except ZeroDivisionError:
				self.change_percent = 'NA'

	temp_val1 = self.price.find('<b>')
	temp_val2 = self.price.find('</b>')
	self.price = self.price[temp_val1+3:temp_val2]
	print self.price
		
			
				
	print 'Time: ' + self.trade_date + ' ' + self.trade_time
	



