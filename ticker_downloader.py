#from pandas_datareader import data


import requests
import pytz
import pandas as pd


from bs4 import BeautifulSoup
from datetime import datetime
#from pandas_datareader import DataReader

#import pandas_datareader.data as web

#import datetime    

from pandas_datareader import data as pdr
import fix_yahoo_finance as yf
yf.pdr_override() # <== that's all it takes :-)

# # download dataframe
# data = pdr.get_data_yahoo("SPY", start="2017-01-01", end="2017-04-30")

# # download Panel
# data = pdr.get_data_yahoo(["SPY", "IWM"], start="2017-01-01", end="2017-04-30")





SITE = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
#START = datetime.datetime(1900, 1, 1)
# END = datetime.datetime(2014, 1, 27)
START = datetime(1900, 1, 1, 0, 0, 0, 0, pytz.utc)
END = datetime.today().utcnow()

def scrape_list(site):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = requests.get(site, headers=hdr)
    soup = BeautifulSoup(req.content,"html.parser")

    table = soup.find('table', {'class': 'wikitable sortable'})
    sector_tickers = dict()
    for row in table.findAll('tr'):
        col = row.findAll('td')
        if len(col) > 0:
            sector = str(col[3].string.strip()).lower().replace(' ', '_')
            ticker = str(col[0].string.strip())
            if sector not in sector_tickers:
                sector_tickers[sector] = list()
            sector_tickers[sector].append(ticker)
    return sector_tickers

def download_ohlc(sector_tickers, start, end):
    sector_ohlc = {}
    for sector, tickers in sector_tickers.items():
        print('Downloading data from Yahoo for %s sector' % sector)
        data = pdr.get_data_yahoo(tickers, start, end, retry_count=20)
# This line commented out due to problem with yahoo and cookies        
#        data = DataReader(tickers, 'yahoo', start, end, retry_count=20)
        for item in ['Open', 'High', 'Low']:
            data[item] = data[item] * data['Adj Close'] / data['Close']
        data.rename(items={'Open': 'open', 'High': 'high', 'Low': 'low',
                           'Adj Close': 'close', 'Volume': 'volume'},
                    inplace=True)
        data.drop(['Close'], inplace=True)
        sector_ohlc[sector] = data
    print('Finished downloading data')
    return sector_ohlc

def store_HDF5(sector_ohlc, path):
    with pd.get_store(path) as store:
        for sector, ohlc in sector_ohlc.items():
            store[sector] = ohlc

def get_snp500():
    sector_tickers = scrape_list(SITE)
    sector_ohlc = download_ohlc(sector_tickers, START, END)
    store_HDF5(sector_ohlc, 'snp500.h5')

if __name__ == '__main__':


    get_snp500()
