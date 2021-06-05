import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import datetime

VALID_TIME_INTERVALS = ["1m","3m","5m","10m","15m","30m","1h","1d"]

class TrendlineTypes(object):
  RESISTANCE = 'RESISTANCE'
  SUPPORT = 'SUPPORT'
  BOTH = 'BOTH'

class CandlestickData():
  def __init__(
    self,
    df=None,
    time_interval="1m", # choose between 1m,3m,5m,10m,15m,30m,1h,1d
    open_col="Open", # name of the column containing candle "Open" price
    high_col="High", # name of the column containing candle "High" price
    low_col="Low", # name of the column containing candle "Low" price
    close_col="Close", # name of the column containing candle "Close" price
    datetime_col=None # name of the column containing candle datetime price (use none if datetime is in index)
  ):
    # Validate dataframe nonempty and has at least 3 entries
    if df is None or len(df)<3:
      raise Exception("CandlestickData constructor param df should have at least three entries, received :\n{}".format(
        df
      ))

    # Validate time interval supplied is correct
    if time_interval not in VALID_TIME_INTERVALS:
      raise Exception("CandlestickData constructor param time_interval must be one of :\n{}".format(
        VALID_TIME_INTERVALS
      ))

    # Price column names provided exist and are in correct format
    for col_name in [open_col, high_col, low_col, close_col]:
      if col_name not in df.columns:
        raise Exception("CandlestickData constructor param df does not contain column '{}'".format(
          col_name
        ))
      if df[col_name].dtypes != float:
        raise Exception("CandlestickData constructor param df requires that column '{}' is of type float".format(
          col_name
        ))

    # Datetime column provide exists and is of type datetime (or index is of type datetime if arg is None)
    if datetime_col == None:
      if not is_datetime(df.index): 
        raise Exception(
          "If no datetime_col is provided to CandlestickData constructor, the df index must be of datetime type.\n" + 
          "Instead received df index of {} type".format(str(type(df.index)))
        )
    else:
      if datetime_col not in df.columns:
        raise Exception("CandlestickData constructor param df does not contain datetime_col '{}'".format(
          datetime_col
        ))
      if not is_datetime(df[datetime_col]):
        raise Exception("CandlestickData constructor param df requires that column '{}' be of type datetime, received {}".format(
          datetime_col, df[datetime_col].dtypes
        ))

    # Instantiate
    self.df = df.copy(deep=True)

    self.df = self.df.rename(columns={
      open_col: "Open",
      high_col: "High",
      low_col: "Low",
      close_col: "Close",
    })

    # Force index to be monotinically increasing int
    if datetime_col == None:
      self.df.set_index(datetime_col)
      self.df = self.df.rename(columns = {'index':'Date'})
    else:
      self.df.rename(columns={datetime_col: "Date"})
    
    self.df.reset_index()

    self.time_interval = time_interval
    self.open_col = open_col
    self.high_col = high_col
    self.low_col = low_col
    self.close_col = close_col
    self.datetime_col = datetime_col

  def time_interval_min(self):
    if 'm' in self.time_interval:
      return int(self.time_interval[:-1])
    elif 'h' in self.time_interval:
      return int(self.time_interval[:-1] * 60)
    elif 'd' in self.time_interval:
      return int(self.time_interval[:-1] * 60 * 24)
