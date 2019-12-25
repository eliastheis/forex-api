import util
import csv
import os
from matplotlib import pyplot as plt
from random import randint
from datetime import datetime
import time
import pytz
from dateutil import parser

#def timestamp_from_date(date): # ist irgendwie falsch (um eine/zwei stunden)
#	return int(time.mktime(datetime.strptime(date + ' UTC', '%d.%m.%Y %H:%M:%S %Z').timetuple()) * 1000)# + 3600000 # adding two hours

def timestamp_from_date(date):
	return parser.parse(date + ' UTC').timestamp()*1000
def date_from_timestamp(timestamp): # ist korrekt
	return str(datetime.fromtimestamp((timestamp)/1000, pytz.UTC)).split('+')[0] # adding one hour

# connect to SQL
host, user, password, database = util.getSqlConfig()
util.connectToSQL(host, user, password, database)

# get files in data-path
files = os.listdir('data')
files = sorted(files)

plt.ion()
data = []

# read files
for file in files:
	with open('data/' + file) as f:
		csv_reader = csv.reader(f)
		next(csv_reader)
		for line in csv_reader:
			#print(line)
			if line[4] != line[3]:
				data.append([timestamp_from_date(line[0].replace('.000', '')),float(line[1]),float(line[2]),float(line[3]),float(line[4])])
	print('loaded:', file)
	
print('first:', date_from_timestamp(data[0][0]), data[0][0])
print('last:', date_from_timestamp(data[-1][0]), data[-1][0])