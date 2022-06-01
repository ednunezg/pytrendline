# pytrendline

## About

Given a OHLC candlestick chart, pytrendline allows you to detect support and resistance lines formed by the High and Close price series.

![pytrendline preview](https://github.com/ednunezg/pytrendline/blob/master/img/about.png)

The trendline scanning algorithm scans for the existence of trendlines by attempting to draw lines between points [(0,1),(0,2),(0,3)...(0,N)] for the first iteration. Subsequent iteration attempts to draw lines between points [(1,2),(1,3),...(1,N)], then [(2,3),(2,4)...(2,N)] and so forth.

Because this operates by doing a full exhaustive search, the runtime is of cubic complexity O(N^3). If low latency is important and your use case is extremely large datasets, you might want to look into alternative algorithms / libraries. For picking up trendlines on day-trading use cases (small number of candles) or offline analysis it works great.

The algorithm also speeds up significantly if the search is narrowed down to only include lines with pivot points as one of the start or end points. 

Note: pivot points are identified as local maximum or minimum points ie “troughs” and “peaks” in the candlestick chart.

## How the algorithm works

1. Pivot points are identified in the candlestick chart.

2. In each scan between points (i,j), pytrendln attempts to draw a line on top of the candlestick chart and checks the following:

* What are the “points” that make up the trendline? For a trendline to be valid it must satisfy the minimum number of points specified in argument `detect(...)` argument `min_points_required`. A date in a trendline is determined to be a valid “point” if the distance between the drawn trendline and the candlestick price does not exceed `max_allowable_error_pt_to_trend`

![Error between trendline and price](https://github.com/ednunezg/pytrendline/blob/master/img/trend_error.png)
		
* Does the trendline cross over a candlestick body somewhere in its trajectory? If the trendline intersects some distance higher `breakout_tolerance` above the candlestick body, we consider this line to be a breakout. Breakout trendlines are only considered valid if `detect(...)` argument `ignore_breakouts` is set to `False`. 

* Checks if the trendline satisfies optional pivot point requirements. If not, the trendline is discarded.

A score is given to the trendline using scoring function specified in `detect(...)` argument `config`. The default scoring function scores trendlines higher if the mean distance between trendline and candle points are low and also gives additional favorability to a higher number of points.

Default scoring function:
```
"scoring_function": lambda candles, err_distances, num_points, slope: (util.avg_candle_range(candles) / util.mean(err_distances)) * (2.5 ** num_points),
```

3. Oftentimes, the trendline search finds trendlines that are almost identical in slope and last price and groups them. Because we might only care about the best scored trendline from each of these groups, the best one is identified and you can choose to discard the rest for your analysis.

![Duplicate grouping](https://github.com/ednunezg/pytrendline/blob/master/img/duplicate_grouping.png)

This grouping is done by 2D clustering the set of (slope,last_price) pairs for all trendlines. Two trendlines are identified to be a part of the same group if both their slopes and last_price are within `duplicate_grouping_threshold_slope` and `duplicate_grouping_threshold_last_price` respectively.


4. Results for all trendlines are returned into an easily sortable and filter-able Pandas dataframe.


## Usage

For detecting trendlines, a Pandas dataframe containing OHLC data must be packaged into a `pytrendline.CandlestickData` object and then passed on to `pytrendline.detect(...)`

```
# Package Candlestick Data
candles_df = pd.read_csv('./fixtures/example.csv')
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

# Detect
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

```

## Tuning algorithm parameters

[DEFAULT_CONFIG within source file detect.py](https://github.com/ednunezg/pytrendline/blob/b01bdb6fccea5aead62d9ac912ab53fefdb0cecd/pytrendline/detect.py#L8) contains default parameters regarding thresholds for pivot detection, trendline detection, grouping, scoring, etc. All of these config parameters are a lambda taking candlestick data as input.

You can override a default by passing a new key string + lambda pair to the `config` parameter in `detect`.

```
results = detect(
   …
   config={
        # Force the tolerance to be derived from last candle price
        "max_allowable_error_pt_to_trend": lambda candles: candles.df.iloc[-1].Close / 100,
   }
)
```

## Plotting results

pytrendline provides a `plot(...)` function to visualize the results in an interactive HTML chart generated with the aid of Bokeh.

```
outf = pytrendline.plot(
  results=results,
  filedir='.',
  filename='example_output.html',
)
os.system("open " + outf)

```

In the resulting plot, pivot points are marked as green diamonds, best trendlines for each duplicate gruop is shown in solid dashed blue/orange, and non-best trendlines are shown in transaparent dotted blue/orange.

## Running example

You can run the example included in this repo to get a taste of what is possible with this library.

1. Clone this github repo into a local directory. 
2. Install required libraries using
	
```
pip install -r requirements.txt 
```

3. Run 
```
python example.py
```

## Installing library

Library can install using pip:

```
pip install pytrendline
```
