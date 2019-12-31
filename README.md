# Forex API
This "API" loads the historical prices from CSV-files downloaded at dukascopy.com.
After this, it gets the price from the live price API fcsapi.com and captures it.
All this data will be saved in SQL. So actually it is no API, but you could easily change it to an API with flask.
This repository is based on [this repository](https://github.com/eliastheis/forex-data-collector).
In this repo, I just downloaded the data from the current year to not exceed the maximum storage (The data from 2003 to 2019 takes over 500mb).

## Dependecies
* mysql-connector (install via pip: 'pip install mysql-connector')

## Usage
To use it, you have to download all the historical data from [dukascopy.com](https://www.dukascopy.com/trading-tools/widgets/quotes/historical_data_feed) and put the CSV-files in the data path.
If you do not want to capture EUR/USD you have to change it in the code (main.py lines 12 and 13).
Besides, you have change the login credentials in the 'sql.con'-file.

If you have done all of this, you now have an SQL table which contains old prices as well as the current price of an exchange rate.