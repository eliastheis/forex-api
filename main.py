import util
import csv
import os
from matplotlib import pyplot as plt
from random import randint
from datetime import datetime
import time
import pytz
from dateutil import parser

symbol = 'eurusd'

def timestamp_from_date(date):
	return int(parser.parse(date + ' UTC').timestamp()*1000)
def date_from_timestamp(timestamp):
	return str(datetime.fromtimestamp((timestamp)/1000, pytz.UTC)).split('+')[0]
def rreplace(s, old, new, occurrence):
	li = s.rsplit(old, occurrence)
	return new.join(li)

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
			if line[4] != line[3]:
				data.append([timestamp_from_date(line[0].replace('.000', '')),float(line[1]),float(line[2]),float(line[3]),float(line[4]),float(line[5])])
	print('loaded:', file)

#check data
length = len(data[0])
for d in data:
	if len(d) != length:
		print('data does not macht:', d)
		exit()

print('first:', date_from_timestamp(data[0][0]), data[0][0])
print('last:', date_from_timestamp(data[-1][0]), data[-1][0])
print(len(data), 'datapoints found')

# add all missing datapoints with unchanged price
current_ms = data[-1][0]
price = data[-1][4]
while current_ms + 60000 < int(round(time.time() * 1000)):
	current_ms += 60000
	data.append([current_ms, price, price, price, price, 0])

# write to SQL
util.executeSQL("CREATE TABLE IF NOT EXISTS " + symbol + " ( `timestamp` BIGINT NOT NULL, `open` FLOAT NOT NULL , `high` FLOAT NOT NULL , `low` FLOAT NOT NULL , `close` FLOAT NOT NULL , `volume` FLOAT NOT NULL , PRIMARY KEY (`timestamp`)) ENGINE = InnoDB; ")
util.executeSQL("TRUNCATE TABLE " + symbol)

current = 0
counter = 0
limit = 1000
cmd = ""
base = "INSERT INTO " + symbol + " (`timestamp`, `open`, `high`, `low`, `close`, `volume`) VALUES "
for i in range(len(data)):
	d = data[i]
	cmd += "('" + str(d[0]) + "', '" + str(d[1]) + "', '" + str(d[2]) + "', '" + str(d[3]) + "', '" + str(d[4]) + "', '" + str(d[5]) + "'),"
	counter += 1
	if counter == limit:
		counter = 0
		util.executeSQL(base + rreplace(cmd, ',', ';', 1))
		cmd = ""
	if round((100*i)/len(data)) != current:
		current = round(100*i/len(data))
		print(str(current) + '%')