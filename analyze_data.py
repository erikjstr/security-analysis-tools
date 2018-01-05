# cython: profile=False

import numpy as np
import sys
import datetime as dt
import pandas as pd
import scipy.signal as signal
from pandas._libs import lib, algos as libalgos
from pandas.core.dtypes.common import _ensure_float64

import matplotlib.pyplot as plt

WINDOW_SIZE=700 # days
AUTOCORR_MAX_DELAY=2
AUTOCORR_DELAY_STEP_SIZE=1

def corr_pandas_frame_like(data_vec, lag):
    numeric_df = data_vec._get_numeric_data()
    cols = numeric_df.columns
    idx = cols.copy()
    mat = numeric_df.values
    correl = libalgos.nanxcorr(_ensure_float64(data_vec),_ensure_float64(data_vec.shift(lag)))
    return pd.DataFrame(correl, index=idx, columns=cols)

def moving_average(data_frame):
    return data_frame.rolling(WINDOW_SIZE,win_type='boxcar').mean()

def xcorr(data):
    
    xcorr_delay={}
    for lag in range(0,AUTOCORR_MAX_DELAY,AUTOCORR_DELAY_STEP_SIZE):
        xcorr_delay[lag]=corr_pandas_frame_like(pct_change, lag)

    return pd.Panel(xcorr_delay)

def save_data(data,output_file="snp_xcorr"):
    now = dt.datetime.now()
    filename='{}_{}{}{}-{}{}.h5'.format(output_file, str(now.year), str(now.month),
                                        str(now.day), str(now.hour), str(now.minute))
    data.to_hdf(filename,'xcorr')

def get_data():
    input_file="snp500.h5"
    data = pd.HDFStore(input_file,'r')
    # Remove sector from data as it is not considered to be important
    daily_closings = pd.concat([data[sector]['close'] for sector in data.keys()],axis=1)

    return daily_closings

def plot_price_and_change(symbol):
    f, (ax1, ax2) = plt.subplots(nrows=2)
    price_data = get_data()
    price_data_ma = moving_average(price_data)
    pct_change = price_data.pct_change()             
    pct_change_ma = moving_average(pct_change)
    ax1 = plt.subplot(2,1,1)
    ax2 = plt.subplot(2,1,2, sharex=ax1)
    ax1.plot(price_data[symbol].dropna())
    ax1.plot(price_data_ma[symbol].dropna())
    ax2.plot(pct_change[symbol].dropna())
    ax2.plot(pct_change_ma[symbol].dropna())
    plt.show()

def aggregate_all():
    price_data_aggregate = get_data().sum(axis=1)
    pct_change = price_data_aggregate.pct_change()
    ax1 = plt.subplot(2,1,1)
    ax2 = plt.subplot(2,1,2, sharex=ax1)
    ax1.plot(price_data_aggregate)
    ax1.plot(moving_average(price_data_aggregate))
    ax2.plot(pct_change)
    ax2.plot(moving_average(pct_change))
    
    plt.show()
    

if __name__ == '__main__':

    
    plot_price_and_change('AMGN')
#    aggregate_all()
    import pdb; pdb.set_trace()

    # xcorr_raw = xcorr(pct_change)
    # xcorr_ma = xcorr(pct_change_ma)
    # pct_change['AAPL'].plot(grid = True)
    # import pdb; pdb.set_trace()
    # save_data(xcorr_data,sys.argv[1])
