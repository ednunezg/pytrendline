import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io

from pytrendline import structs

def get_candlestick_data(time_interval, csv_string):
  df = get_candlestick_df(csv_string)
  cdata = structs.CandlestickData(
    df=df,
    time_interval=time_interval,
    open_col="Open",
    high_col="High",
    low_col="Low",
    close_col="Close",
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
Date                         Idx     Low     High     Open   Close   Volume
2019-07-22T09:30:00-04:00    0       200.05  250.01   240    245     100000
2019-07-22T09:35:00-04:00    1       200.03  250.02   240    245     100000
2019-07-22T09:40:00-04:00    2       200.02  249.98   240    245     100000
2019-07-22T09:45:00-04:00    3       199.95  250.01   240    245     100000
2019-07-22T09:50:00-04:00    4       200.01  249.96   240    245     100000
2019-07-22T09:55:00-04:00    5       100     300      240    245     100000
''')

NO_TREND_5m = get_candlestick_data('5m', '''
Date                         Idx     Low     High   Open   Close   Volume
2019-07-22T09:30:00-04:00    0       200     240    215    217     100000
2019-07-22T09:35:00-04:00    1       210     230    215    217     100000
2019-07-22T09:40:00-04:00    2       211     231    215    217     100000
2019-07-22T09:45:00-04:00    3       200     250    235    237     100000
2019-07-22T09:50:00-04:00    4       210     240    235    237     100000
2019-07-22T09:55:00-04:00    5       211     251    235    237     100000
''')

NO_TREND_1d = get_candlestick_data('1d', '''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     240    215    217     100000
2019-07-23     1       210     230    215    217     100000
2019-07-24     2       211     231    215    217     100000
2019-07-25     3       200     250    235    237     100000
2019-07-26     4       210     240    235    237     100000
2019-07-27     5       211     251    235    237     100000
''')

SUP_6pt_TREND_5m = get_candlestick_data('5m','''
Date                  Idx     Low     High   Open   Close     Volume
2019-07-22T09:30:00     0       200     250    210    220     100000
2019-07-23T09:35:00     1       201     230    210    220     100000
2019-07-24T09:40:00     2       202     231    210    220     100000
2019-07-25T09:45:00     3       203     230    210    220     100000
2019-07-26T09:50:00     4       204     240    210    220     100000
2019-07-27T09:55:00     5       205     301    210    220     100000
''')

SUP_6pt_TREND_1d = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     250    210    220     100000
2019-07-23     1       201     230    210    220     100000
2019-07-24     2       202     231    210    220     100000
2019-07-25     3       203     230    210    220     100000
2019-07-26     4       204     240    210    220     100000
2019-07-27     5       205     301    210    220     100000
''')

RES_6pt_TREND_1d = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     299    240    260     100000
2019-07-23     1       190     298    240    260     100000
2019-07-24     2       211     297    240    260     100000
2019-07-25     3       220     296    240    260     100000
2019-07-26     4       230     295    240    260     100000
2019-07-27     5       190     294    240    260     100000
''')

SUP_3pt_TREND_1d = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       100     240    225    226     100000
2019-07-23     1       230     240    235    236     100000
2019-07-24     2       200     250    225    226     100000
2019-07-25     3       201     230    225    226     100000
2019-07-26     4       202     240    225    226     100000
2019-07-27     5       220     240    225    226     100000
2019-07-28     6       221     320    225    226     100000
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
2019-07-22     0       200     300    240    260     100000
2019-07-23     1       210     300    240    260     100000
2019-07-24     2       211     398    240    260     100000
2019-07-25     3       220     397    240    260     100000
2019-07-26     4       230     396    240    260     100000
2019-07-27     5       360     365    362    363     100000
''')

ONE_RES_LINE_WITHOUT_GLOBAL_MAX_1d = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       200     450    240    260     100000
2019-07-23     1       210     300    240    260     100000
2019-07-24     2       211     398    240    260     100000
2019-07-25     3       220     397    240    260     100000
2019-07-26     4       230     396    240    260     100000
2019-07-27     5       280     350    320    330     100000
''')

FLAT_RES_AND_SUP = get_candlestick_data('1d','''
Date           Idx     Low     High   Open   Close   Volume
2019-07-22     0       230     270    240    260     100000
2019-07-23     1       200     300.02 240    260     100000
2019-07-24     2       199.97  270    240    260     100000
2019-07-25     3       230     299.99 240    260     100000
2019-07-26     4       200.02  270    240    260     100000
2019-07-27     5       230     300    240    260     100000
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