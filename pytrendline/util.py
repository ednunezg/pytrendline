# Find the set of maximums and minimums in a series,
# with some tolerance for multiple max or minimums 
# if some highest or lowest values in a series are
# tolerance_threshold away
def find_maxs_or_mins_in_series(series, kind, tolerance_threshold):
  isolated_globals = []
  if kind == "max":
    global_max_or_min = series.max()
  else:
    global_max_or_min = series.min()
  
  for idx, val in series.items():
    if val == global_max_or_min or abs(global_max_or_min - val ) < tolerance_threshold:
      isolated_globals.append(idx)
  return isolated_globals

# Find the average distance between High and Low price in a set of candles
def avg_candle_range(candles):
  return max((candles.df.High - candles.df.Low).mean(), 0.01)

# Find mean in a list of int or floats
def mean(ls):
  total = 0
  for n in ls: total+=n
  return total/len(ls)