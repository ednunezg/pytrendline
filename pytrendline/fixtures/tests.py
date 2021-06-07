import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io

from .. import structs

def get_candlestick_data(time_interval, csv_string):
  df = get_candlestick_df(csv_string)
  cdata = structs.CandlestickData(
    df=df,
    time_interval=time_interval,
    open_col="Open",
    high_col="High",
    low_col="Low",
    close_col="Close", # name of the column containing candle "Close" price
    datetime_col="Date"
  )
  return cdata


def get_candlestick_df(csv_string):
  csv_string = csv_string.strip()

  df = pd.read_csv(io.StringIO(csv_string), delim_whitespace=True)
  df.Idx    = df.Idx.astype(int)
  df.Open   = df.Open.astype(float)
  df.Close  = df.Close.astype(float)
  df.High   = df.High.astype(float)
  df.Low    = df.Low.astype(float)
  df.Volume = df.Volume.astype(int)

  df.set_index('Idx')
  df.reset_index(level=0, inplace=True)

  df['Date'] = pd.to_datetime(df['Date'])
  return df


# Trendline exists, but not detected due to breakout
NO_TREND_DUE_BREAKOUT_5m = get_candlestick_data('5m', '''
Date                         Idx     Low     High   Open   Close   Volume
2019-07-22T09:30:00-04:00    0       200     300    240    260     100000
2019-07-22T09:35:00-04:00    1       200     300    240    260     100000
2019-07-22T09:40:00-04:00    2       200     300    240    260     100000
2019-07-22T09:45:00-04:00    3       200     300    240    260     100000
2019-07-22T09:50:00-04:00    4       200     300    240    260     100000
2019-07-22T09:55:00-04:00    5       100     400    240    260     100000
''')

NO_TREND_5m = get_candlestick_data('5m', '''
Date                         Idx     Low     High   Open   Close   Volume
2019-07-22T09:30:00-04:00    0       200     300    240    260     100000
2019-07-22T09:35:00-04:00    1       210     310    240    260     100000
2019-07-22T09:40:00-04:00    2       211     311    240    260     100000
2019-07-22T09:45:00-04:00    3       220     310    240    260     100000
2019-07-22T09:50:00-04:00    4       230     320    240    260     100000
2019-07-22T09:55:00-04:00    5       231     321    240    260     100000
''')

NO_TREND_1d = get_candlestick_data('1d', '''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     300    240    260     100000
2019-07-23     1       210     310    240    260     100000
2019-07-24     2       211     311    240    260     100000
2019-07-25     3       220     310    240    260     100000
2019-07-26     4       230     320    240    260     100000
2019-07-27     5       231     321    240    260     100000
''')

SUP_6pt_TREND_5m = get_candlestick_data('5m','''
Date                  Idx     Low     High   Open   Close     Volume
2019-07-22T09:30:00     0     200     300    240    260       100000
2019-07-23T09:35:00     1     201     310    240    260       100000
2019-07-24T09:40:00     2     202     311    240    260       100000
2019-07-25T09:45:00     3     203     310    240    260       100000
2019-07-26T09:50:00     4     204     320    240    260       100000
2019-07-27T09:55:00     5     205     321    240    260       100000
''')

SUP_6pt_TREND_1d = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     300    240    260     100000
2019-07-23     1       201     310    240    260     100000
2019-07-24     2       202     311    240    260     100000
2019-07-25     3       203     310    240    260     100000
2019-07-26     4       204     320    240    260     100000
2019-07-27     5       205     321    240    260     100000
''')

RES_6pt_TREND_1d = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     299    240    260     100000
2019-07-23     1       210     298    240    260     100000
2019-07-24     2       211     297    240    260     100000
2019-07-25     3       220     296    240    260     100000
2019-07-26     4       230     295    240    260     100000
2019-07-27     5       231     294    240    260     100000
''')

SUP_3pt_TREND_1d = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       100     300    240    260     100000
2019-07-23     1       230     310    240    260     100000
2019-07-24     2       200     310    240    260     100000
2019-07-25     3       201     311    240    260     100000
2019-07-26     4       202     310    240    260     100000
2019-07-27     5       220     320    240    260     100000
2019-07-28     6       221     321    240    260     100000
'''
)

ONE_SUP_TREND_IN_FIRST_THREE_INDECES = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     300    240    260     100000
2019-07-23     1       201     310    240    260     100000
2019-07-24     2       202     311    240    260     100000
2019-07-25     3       220     310    240    260     100000
2019-07-26     4       221     320    240    260     100000
2019-07-27     5       230     321    240    260     100000
'''
)

ONE_SUP_AND_ONE_RES_TREND_1d = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     299    240    260     100000
2019-07-23     1       201     298    240    260     100000
2019-07-24     2       202     297    240    260     100000
2019-07-25     3       203     296    240    260     100000
2019-07-26     4       204     295    240    260     100000
2019-07-27     5       205     294    240    260     100000
''')

TWO_SUP_AND_ONE_RES_TREND_1d = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     299    240    260     100000
2019-07-23     1       201     298    240    260     100000
2019-07-24     2       202     297    240    260     100000
2019-07-25     3       230     296    240    260     100000
2019-07-26     4       220     295    240    260     100000
2019-07-27     5       221     294    240    260     100000
2019-07-28     6       222     293    240    260     100000
''')

ONE_RES_LINE_WITH_GLOBAL_MAX_1d = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     400    240    260     100000
2019-07-23     1       210     300    240    260     100000
2019-07-24     2       211     300    240    260     100000
2019-07-25     3       220     397    240    260     100000
2019-07-26     4       230     396    240    260     100000
2019-07-27     5       231     300    240    260     100000
''')

ONE_RES_LINE_WITHOUT_GLOBAL_MAX_1d = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     450    240    260     100000
2019-07-23     1       210     300    240    260     100000
2019-07-24     2       211     398    240    260     100000
2019-07-25     3       220     397    240    260     100000
2019-07-26     4       230     396    240    260     100000
2019-07-27     5       231     300    240    260     100000
''')

FLAT_RES_AND_SUP = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     300    240    260     100000
2019-07-23     1       200     300    240    260     100000
2019-07-24     2       200     300    240    260     100000
2019-07-25     3       200     300    240    260     100000
2019-07-26     4       200     300    240    260     100000
2019-07-27     5       200     300    240    260     100000
''')

ONE_PIVOT_LOW_AND_HIGH = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume    Notes
2019-07-22     0       190     300    240    260     100000    <---This_is_low+high_pivot
2019-07-23     1       200     300    240    260     100000    
2019-07-24     2       150     300    240    260     100000    <---This_is_low_pivot
2019-07-25     3       200     350    240    260     100000    <---This_is_high_pivot
2019-07-26     4       200     300    240    260     100000    
2019-07-27     5       180     340    240    260     100000    <---This_is_low+high_pivot
''')


NO_PIVOTS_EXCEPT_FOR_START_END = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       180     320    240    260     100000
2019-07-23     1       200     300    240    260     100000
2019-07-24     2       200     300    240    260     100000
2019-07-25     3       200     300    240    260     100000
2019-07-26     4       200     300    240    260     100000
2019-07-27     5       180     320    240    260     100000
''')