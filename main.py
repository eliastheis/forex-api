import util
import csv
from os import listdir
from datetime import datetime
import time
import pytz
from dateutil import parser
import requests
import json

symbol = 'eurusd' # format 'eurusd'
symbol_upper = 'EUR/USD' # format 'EUR/USD'

def timestamp_from_date(date):
	return int(parser.parse(date + ' UTC').timestamp()*1000)
def date_from_timestamp(timestamp):
	return str(datetime.fromtimestamp((timestamp)/1000, pytz.UTC)).split('+')[0]
def rreplace(s, old, new, occurrence):
	li = s.rsplit(old, occurrence)
	return new.join(li)
def getPrice(symbol, old_price):
	try:
		data = requests.get('https://fcsapi.com/api/forex/latest?symbol=' + symbol + '&access_key=ulz8KI9wbwTVY2b2BBtUjhoJFDFhyndoqOpmvXqbLuTDGOV9Vu').text
		data = json.loads(data)
		if data['status'] == True:
			return float(data['response'][0]['price'])
		else:
			return old_price
	except Exception as e:
		print('## EXCEPTION ##')
		print(e)
		return old_price

# connect to SQL
host, user, password, database = util.getSqlConfig()
util.connectToSQL(host, user, password, database)

# get files in data-path
files = listdir('data')
files = sorted(files)

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
limit = 10000
cmd = ""
base = "INSERT INTO " + symbol + " (`timestamp`, `open`, `high`, `low`, `close`, `volume`) VALUES "
#all_timestamps = []
latest_timestamp = 0
tmp = False
for i in range(len(data)):
	d = data[i]
	if d[0] > latest_timestamp:
		latest_timestamp = d[0]
		cmd += "('" + str(d[0]) + "', '" + str(d[1]) + "', '" + str(d[2]) + "', '" + str(d[3]) + "', '" + str(d[4]) + "', '" + str(d[5]) + "'),"
		counter += 1
		if counter == limit:
			counter = 0
			util.executeSQL(base + rreplace(cmd, ',', ';', 1))
			cmd = ""
			#all_timestamps = all_timestamps[len(all_timestamps)-87000:]
	if round((100*i)/len(data)) != current:
		current = round(100*i/len(data))
		util.p('LOADS', str(current) + '%')
util.executeSQL(base + rreplace(cmd, ',', ';', 1))

# get live data from fcsapi.com
open = data[-1][4]
high = open
low = open
close = open
last_ms = data[-1][0]
time_step = 60000 # one minute

next_update_ms = last_ms + time_step

while True:
	
	# check for update
	if int(round(time.time() * 1000)) > next_update_ms:
		util.p('PRICE', date_from_timestamp(next_update_ms) + ' ' + str(open) + ' ' + str(high) + ' ' + str(low) + ' ' + str(close))
		util.executeSQL(base + "('" + str(next_update_ms) + "', '" + str(open) + "', '" + str(high) + "', '" + str(low) + "', '" + str(close) + "', '" + str(1) + "');")
		next_update_ms += time_step
		open = close
		high = close
		low = close
	
	# update price
	close = getPrice(symbol_upper, close)
	if close > high:
		high = close
	if close < low:
		low = close
	
	time.sleep(6)