def find_maxs_or_mins_in_series(series, type, tolerance_threshold):
  isolated_globals = []
  if type == "max":
    global_max_or_min = series.max()
  else:
    global_max_or_min = series.min()
  
  for idx, val in series.items():
    if val == global_max_or_min or abs(global_max_or_min - val ) < tolerance_threshold:
      isolated_globals.append(idx)
  return isolated_globals

def avg_candle_range(candles):
  return max((candles.df.High - candles.df.Low).mean(), 0.01)

def mean(ls):
  total = 0
  for n in ls: total+=n
  return total/len(ls)