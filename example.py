import pytrendline
import pandas as pd
import os
import time

# 1. Construct candlestick data. This example just grabs data from a fixture
candles_df = pd.read_csv('./fixtures/example.csv')
candles_df.set_index('Idx')
candles_df['Date'] = pd.to_datetime(candles_df['Date'])


candlestick_data = pytrendline.CandlestickData(
  df=candles_df,
  time_interval="1m", # choose between 1m,3m,5m,10m,15m,30m,1h,1d
  open_col="Open", # name of the column containing candle "Open" price
  high_col="High", # name of the column containing candle "High" price
  low_col="Low", # name of the column containing candle "Low" price
  close_col="Close", # name of the column containing candle "Close" price
  datetime_col="Date" # name of the column containing candle datetime price (use none if datetime is in index)
)

print("📈 📉 Starting call to pytrendline.detect ... (this could take a while on a large candlestick dataset)")

detect_start_time = time.time()

# 2. Find trendlines. Results are returned in the form of
#     a. A pandas dataframe table containing trendline found per row
#     b. A pandas series containing pivot points
results = pytrendline.detect(
  candlestick_data=candlestick_data,

  # Choose between BOTH, SUPPORT or RESISTANCE
  trend_type=pytrendline.TrendlineTypes.BOTH,
  # Specify if you require the first point of a trendline to be a pivot
  first_pt_must_be_pivot=False,
  # Specify if you require the last point of the trendline to be a pivot
	last_pt_must_be_pivot=False,
	# Specify if you require all trendline points to be pivots
  all_pts_must_be_pivots=False,
	# Specify if you require one of the trendline points to be global max or min price
  trendline_must_include_global_maxmin_pt=False,
  # Specify minimum amount of points required for trendline detection (NOTE: must be at least two)
  min_points_required=3,
  # Specify if you want to ignore prices before some date
  scan_from_date=None,
  # Specify if you want to ignore 'breakout' lines. That is, lines that interesect a candle
  ignore_breakouts=True,
  # Specify and override to default config (See docs on how)
  config={}
)

detect_end_time = time.time()

print("✅ pytrendline.detect took {:.4f}s".format(detect_end_time - detect_start_time))

# 3. Plot the trendlines found
outf = pytrendline.plot(
  results=results,
  filedir='.',
  filename='example_output.html',
)

print("💾 Trendline results saved in {}".format(outf))
os.system("open " + outf)