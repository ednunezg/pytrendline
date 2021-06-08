import numpy as np
import pandas as pd
import sys

from . import util
from . import structs

DEFAULT_CONFIG = {
  # For some price at date t, what difference must be exceeded between p_t-1 and p_t+1
  # with respsect to p_t for t to be considered pivot
  "pivot_seperation_threshold": lambda candles: util.avg_candle_range(candles) * 0.2,

  # For some pivot found at date t, what difference is tolerable between p_t-1 to p_t and p_t+1 to p_t
  # for either p_t-1 or p_t+1 to ALSO be considered pivots
  "pivot_grouping_threshold": lambda candles: util.avg_candle_range(candles) * 0.1,

  # Max allowable error for a trendline point and a candlestick price
  "max_allowable_error_pt_to_trend": lambda candles: util.avg_candle_range(candles) * 0.1,
  
  # After trendlines have been found, the slopes and last prices for each trendline are collected in a 2D
  # array. We use 2D clustering of (slope,last_price) to find 'duplicates' ie almost identical trendlines
  # Below are the thresholds for grouping last price and slope
  "duplicate_grouping_threshold_last_price": lambda candles: util.avg_candle_range(candles) * 0.2,
  "duplicate_grouping_threshold_slope": lambda candles: util.avg_candle_range(candles) * 0.05,

  # How much does a trendline break into any candle for it to be considered a break-out
  "breakout_tolerance": lambda candles: util.avg_candle_range(candles) * 0.08,

  # Scores a detected trendline given a slice of distance from trend to price, slope, and candlesticks
  "scoring_function": lambda candles, err_distances, num_points, slope: (util.avg_candle_range(candles) / util.mean(err_distances)) * (2.5 ** num_points),

  # Max and min allowable slope angle for both resistance and support lines
  # By default set to allow all angles but min or max can be set to 0 to only allow possitive / negative slopes
  'max_allowable_support_slope': lambda candles: sys.float_info.max,
  'min_allowable_support_slope': lambda candles: -sys.float_info.max,
  'max_allowable_resistance_slope': lambda candles: sys.float_info.max,
  'min_allowable_resistance_slope': lambda candles: -sys.float_info.max,

  # Max and min allowable last price point for both resistance and support lines
  # By default set to be 1.5X of last candle closing price for max and 0.667x for min 
  'max_allowable_support_last_price': lambda candles: candles.df.Close.iloc[-1] * 1.5,
  'min_allowable_support_last_price': lambda candles: candles.df.Close.iloc[-1] * 0.667,
  'max_allowable_resistance_last_price': lambda candles: candles.df.Close.iloc[-1] * 1.5,
  'min_allowable_resistance_last_price': lambda candles: candles.df.Close.iloc[-1] * 0.667,
}

def get_pivots(
  candlestick_data=None,
  trend_type=None,
  scan_from_index=None,
  config=DEFAULT_CONFIG,
  debug=False
):
  if candlestick_data == None:
    raise Exception("No candlestick data provided")
  elif type(candlestick_data) != structs.CandlestickData:
    raise Exception("candlestick_data input provided is of invalid type. See README for instructions")

  if trend_type == None:
    raise Exception("No trend_type data provided")
  elif type(trend_type) != str:
    raise Exception("trend_type input provided is of invalid type. See README for instructions")

  separation_thres = config.get('pivot_seperation_threshold', DEFAULT_CONFIG['pivot_seperation_threshold'])(candlestick_data)
  grouping_thres = config.get('pivot_grouping_threshold', DEFAULT_CONFIG['pivot_grouping_threshold'])(candlestick_data)

  col = "Low" if trend_type == structs.TrendlineTypes.SUPPORT else "High"  
  pseries = candlestick_data.df[col][scan_from_index:]
  pivots = set([])
  max_number_continuous_pivots = 6

  first_index = pseries.index[0]
  last_index = pseries.index[-1]

  for i in range(first_index+1,last_index):
    pcur = pseries[i]
    pprev = pseries[i-1]

    j = 1
    while j < max_number_continuous_pivots and (i + j) < len(pseries) - 1:
      if abs(pseries[i + j - 1] - pseries[i + j]) < grouping_thres:
        j += 1
      else:
        break

    pnext = pseries[i + j]

    j = 1
    while j < max_number_continuous_pivots and (i - j) > first_index:
      if abs(pseries[i - j + 1] - pseries[i - j]) < grouping_thres:
        j += 1
      else:
        break
    
    pprev = pseries[i - j]

    if trend_type == structs.TrendlineTypes.RESISTANCE and \
      (pprev > pcur or pnext > pcur): continue
    elif trend_type == structs.TrendlineTypes.SUPPORT and \
      (pprev < pcur or pnext < pcur): continue

    if abs(pcur - pprev) > separation_thres * (1/4) and abs(pcur - pnext) > separation_thres * (3/4):
      pivots.add(i)
    elif abs(pcur - pprev) > separation_thres * (3/4) and abs(pcur - pnext) > separation_thres * (1/4):
      pivots.add(i)

  # Always include last point and first point as pivots
  pivots.add(first_index)
  pivots.add(last_index)

  if debug:
    print(
      "🐛 FIND PIVOT DEBUG 🐛\n" + \
      "Grouping Threshold = {}\n".format(grouping_thres) + \
      "Separation Threshold = {}\n".format(separation_thres) + \
      "Pivots found = {}\n".format(pivots) + \
      "Percentage of pivots to total data points = {}\n".format(((len(pivots) / len(pseries))) * 100 )
    )
    
  return pivots


def detect(
  candlestick_data=None,
  trend_type=None,

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

  # Specify config for tuning detection/grouping/scoring parameters
  config=DEFAULT_CONFIG,

  # Console print debugs
  debug=False
):
  def detect_wrapped(tt):
    '''
    The algorithm will fly through all N^2 pivot point pairs,
    then it attempts to draw an aproximation line through each pair
    and will find this line to be a valid trendline iff this line contains
    points within config.max_allowable_error_pt_to_trend and and a total point
    quantity of min_points_required

    After all trendlines are retrieved:
      - Retrieve score
      - Detect which of the trendlines are duplicate (ie their slope and intercept are almost identical)
        and mark the one with best score

    '''
    # Input validation
    if candlestick_data == None:
      raise Exception("No candlestick data provided")
    elif type(candlestick_data) != structs.CandlestickData:
      raise Exception("candlestick_data input provided is of invalid type. See README for instructions")

    if tt == None:
      raise Exception("No trend_type data provided")
    elif type(tt) != str:
      raise Exception("trend_type input provided is of invalid type. See README for instructions")

    # Process config
    max_allowable_error_pt_to_trend = config.get("max_allowable_error_pt_to_trend", DEFAULT_CONFIG["max_allowable_error_pt_to_trend"])(candlestick_data)
    breakout_tolerance = config.get("breakout_tolerance", DEFAULT_CONFIG["breakout_tolerance"])(candlestick_data)
    max_allowable_support_slope = config.get("max_allowable_support_slope", DEFAULT_CONFIG["max_allowable_support_slope"])(candlestick_data)
    min_allowable_support_slope = config.get("min_allowable_support_slope", DEFAULT_CONFIG["min_allowable_support_slope"])(candlestick_data)
    max_allowable_resistance_slope = config.get("max_allowable_resistance_slope", DEFAULT_CONFIG["max_allowable_resistance_slope"])(candlestick_data)
    min_allowable_resistance_slope = config.get("min_allowable_resistance_slope", DEFAULT_CONFIG["min_allowable_resistance_slope"])(candlestick_data)
    max_allowable_support_last_price = config.get("max_allowable_support_last_price", DEFAULT_CONFIG["max_allowable_support_last_price"])(candlestick_data)
    min_allowable_support_last_price = config.get("min_allowable_support_last_price", DEFAULT_CONFIG["min_allowable_support_last_price"])(candlestick_data)
    max_allowable_resistance_last_price = config.get("max_allowable_resistance_last_price", DEFAULT_CONFIG["max_allowable_resistance_last_price"])(candlestick_data)
    min_allowable_resistance_last_price = config.get("min_allowable_resistance_last_price", DEFAULT_CONFIG["min_allowable_resistance_last_price"])(candlestick_data)

    max_allowable_slope = max_allowable_support_slope if tt == structs.TrendlineTypes.SUPPORT else max_allowable_resistance_slope
    min_allowable_slope = min_allowable_support_slope if tt == structs.TrendlineTypes.SUPPORT else min_allowable_resistance_slope
    max_allowable_last_price = max_allowable_support_last_price if tt == structs.TrendlineTypes.SUPPORT else max_allowable_resistance_last_price
    min_allowable_last_price = min_allowable_support_last_price if tt == structs.TrendlineTypes.SUPPORT else min_allowable_resistance_last_price

    if scan_from_date != None:
      scan_from_index = candlestick_data.df.loc[candlestick_data.df["Date"] == scan_from_date]
    else:
      scan_from_index = candlestick_data.df.loc[0].name

    col = "Low" if tt == structs.TrendlineTypes.SUPPORT else "High"  
    pseries = candlestick_data.df[col][scan_from_index:]
    pseries_sub = pseries[scan_from_index:]

    last_index = len(candlestick_data.df) - 1
    last_price = pseries[len(candlestick_data.df) - 1]
    time_interval_min = candlestick_data.time_interval_min()

    pivots = get_pivots(candlestick_data, tt, scan_from_index, config)
    pivots_sorted = list(pivots)
    pivots_sorted.sort()

    avg_candle_range = util.avg_candle_range(candlestick_data)

    # Threshold to decide max difference from a global max/min and consecutive best next global max/min to both be considered
    max_or_min_capture_thres = avg_candle_range * 0.10
    global_max_or_mins = []
    if tt == structs.TrendlineTypes.RESISTANCE:
      global_max_or_mins = util.find_maxs_or_mins_in_series(pseries_sub, "max", max_or_min_capture_thres)
    else:
      global_max_or_mins = util.find_maxs_or_mins_in_series(pseries_sub, "min", max_or_min_capture_thres)

    # Trendlines is a pandas dataframe containing columns ( slice_of_points, num_points, slope, intercept, score)
    trends_df = pd.DataFrame(columns=[
      'id',
      'trendtype',
      'pointset_indeces',
      'pointset_dates',
      'starts_at_index',
      'starts_at_date',
      'ends_at_index',
      'ends_at_date',
      'is_breakout',
      'breakout_index',
      'breakout_date',
      'num_points',
      'm',
      'b',
      'slope',
      'price_at_last_date',
      'score',
      'includes_global_max_or_min',
      'global_maxs_or_mins',
      'price_at_next_future_date',
      'duplicate_group_id',
      'is_best_from_duplicate_group',
      'overall_rank',
      'rank_within_group',
    ])
    
    for i in range(0, len(pseries)):
      # If we only specify using pivot points as start, skip non pivots
      if (first_pt_must_be_pivot or all_pts_must_be_pivots) and i not in pivots:
          continue

      # Skip indeces after opts.scan_from_index
      if scan_from_index > i:
        continue

      for j in range(i+1, len(pseries)):
        # If we only specify using pivot points as end, skip non pivots
        if (last_pt_must_be_pivot or all_pts_must_be_pivots) and j not in pivots:
            continue

        iprice = pseries[i]
        jprice = pseries[j]

        # Find the slope and intercept made formed by these two points
        m, b = np.polyfit([i, j], [iprice, jprice], 1)

        # Slope is found by considering time_interval_min as rightward unit and average candle range as upward unit
        slope = m * avg_candle_range
      
        # Check if the estimated price at last date or slope is allowable
        trend_price_at_last = m * last_index + b


        if slope > max_allowable_slope or slope < min_allowable_slope:
          continue

        if trend_price_at_last > max_allowable_last_price or trend_price_at_last < min_allowable_last_price:
          continue

        # Determine breakouts + count the number of points within this trendline
        num_points = 2
        points_in_trendline = [i, j]
        prices_in_trendline = [m * i + b, m * j + b]
        is_breakout = False
        breakout_index = None
        breakout_date = None

        for k in range(i, len(pseries)):
          if last_pt_must_be_pivot and k not in pivots:
            continue

          # Skip checking for the i or j case because these are already points in the set
          if k == i or k == j:
            continue

          trend_price_at_k = m * k + b

          # Determine if this trend is a breakout, if it hasn't been identified as one already
          if not is_breakout:
            if tt == structs.TrendlineTypes.RESISTANCE and trend_price_at_k < pseries[k] - breakout_tolerance or \
                tt == structs.TrendlineTypes.SUPPORT and trend_price_at_k > pseries[k] + breakout_tolerance:

              breakout_index = k
              breakout_date = candlestick_data.df.iloc[i].Date
              is_breakout = True
            

          if abs(trend_price_at_k - pseries[k]) < max_allowable_error_pt_to_trend:
            num_points += 1
            points_in_trendline.append(k)
            prices_in_trendline.append(trend_price_at_k)

        # Check if we have the minimum required number of points for trend
        if num_points < min_points_required: continue

        # Construct a "pointset_id" a unique identifier for this set of points
        points_in_trendline.sort()
        points_in_trendline_str = ('[' + str(points_in_trendline[0]))
        for p in range(1, len(points_in_trendline)):
          points_in_trendline_str += ("," + str(points_in_trendline[p]))
        points_in_trendline_str += "]"
        pointset_id = ("R" if tt == structs.TrendlineTypes.RESISTANCE else "S") + "-" + points_in_trendline_str

        # Determine if trendline has max or min, and skip this line if we require our lines have global max or min
        global_pt_found = False
        for p in points_in_trendline:
          if p in global_max_or_mins:
            global_pt_found = True

        if trendline_must_include_global_maxmin_pt and not global_pt_found:
          continue

        # We already have this pointset, just different order
        if pointset_id in trends_df.id.values: continue

        # We ignore this i,j pair if this is a breakout
        if is_breakout and ignore_breakouts: continue

        # Scoring
        err_distances = []
        for w in range(0,num_points):
          point_index = points_in_trendline[w]
          price_at_trendline = prices_in_trendline[w]
          price_actual = pseries[point_index]
          err_distances.append(abs(price_at_trendline - price_actual))
        
        score = config.get("scoring_function", DEFAULT_CONFIG["scoring_function"])(candlestick_data, err_distances, num_points, slope)
        
        trends_df = trends_df.append({
          'id':              pointset_id,
          'trendtype':       tt,
          'pointset_indeces':points_in_trendline,
          'pointset_dates':  [candlestick_data.df.iloc[pt].Date for pt in points_in_trendline],
          'starts_at_index': points_in_trendline[0],
          'starts_at_date':  candlestick_data.df.iloc[points_in_trendline[0]].Date,
          'ends_at_index':   points_in_trendline[-1],
          'ends_at_date':    candlestick_data.df.iloc[points_in_trendline[-1]].Date,
          'is_breakout':     is_breakout,
          'breakout_index':  breakout_index,
          'breakout_date':   breakout_date,
          'num_points':      num_points,
          'm': m,
          'b': b,
          'slope': slope,
          'price_at_last_date': trend_price_at_last,
          'score': score,
          'global_maxs_or_mins': global_max_or_mins,
          'includes_global_max_or_min': global_pt_found,
          'price_at_next_future_date': trend_price_at_last + m,
          'duplicate_group_id': None,
          'is_best_from_duplicate_group': False,
          'overall_rank': None,
          'rank_within_group': 0
        }, ignore_index=True)

    # Mark which of the trendlines are duplicate
    trends_df = _mark_duplicates(trends_df, candlestick_data, tt, config)
    trends_df = trends_df.sort_values(by='score', ascending=False)

    # Correct data types
    trends_df["is_breakout"] = trends_df["is_breakout"].astype(bool)

    return trends_df, pivots


  if trend_type == structs.TrendlineTypes.BOTH:
    support_trendlines, support_pivots = detect_wrapped(structs.TrendlineTypes.SUPPORT)
    resistance_trendlines, resistance_pivots = detect_wrapped(structs.TrendlineTypes.RESISTANCE)

    return {
      'trend_type': trend_type,
      'candlestick_data': candlestick_data,
      'support_pivots': support_pivots,
      'support_trendlines': support_trendlines,
      'resistance_pivots': resistance_pivots,
      'resistance_trendlines': resistance_trendlines,
    }
  elif trend_type == structs.TrendlineTypes.SUPPORT:
    support_trendlines, support_pivots = detect_wrapped(structs.TrendlineTypes.SUPPORT)

    return {
      'trend_type': trend_type,
      'candlestick_data': candlestick_data,
      'support_pivots': support_pivots,
      'support_trendlines': support_trendlines,
    }
  else:
    resistance_trendlines, resistance_pivots = detect_wrapped(structs.TrendlineTypes.RESISTANCE)

    return {
      'trend_type': trend_type,
      'candlestick_data': candlestick_data,
      'resistance_pivots': resistance_pivots,
      'resistance_trendlines': resistance_trendlines
    }

def _mark_duplicates(trends_df, candlestick_data, trend_type, config):
  duplicate_grouping_threshold_last_price = config.get("duplicate_grouping_threshold_last_price", DEFAULT_CONFIG['duplicate_grouping_threshold_last_price'])(candlestick_data)
  duplicate_grouping_threshold_slope = config.get("duplicate_grouping_threshold_slope", DEFAULT_CONFIG['duplicate_grouping_threshold_slope'])(candlestick_data)
  
  if len(trends_df) == 0: return trends_df

  if len(trends_df) == 1:
    trends_df.loc[0, 'duplicate_group_id'] = 1000
    trends_df.loc[0, 'is_best_from_duplicate_group'] = True
    trends_df.loc[0, 'overall_rank'] = 1
    trends_df.loc[0, 'rank_within_group'] = 1
    return trends_df

  group_idx = 1000 if trend_type == structs.TrendlineTypes.RESISTANCE else 2000

  # 2D clustering last price and slope to find closely related trendlines
  for i in range(0, len(trends_df)):
    best_matching_idx = -1
    row_i = trends_df.iloc[i]
    row_last_price = row_i['price_at_last_date']
    row_slope_angle = row_i['slope']
    i_is_breakout = row_i['is_breakout']

    for j in range(0, len(trends_df)):
      if i==j: continue

      row_j = trends_df.iloc[j]
      sec_row_last_price = row_j['price_at_last_date']
      sec_row_slope_angle = row_j['slope']
      j_is_breakout = row_j['is_breakout']

      price_diff = abs(row_last_price - sec_row_last_price)
      slope_angle_diff = abs(row_slope_angle - sec_row_slope_angle)

      # We determine that row i and row j are a good match for same group
      if ((price_diff < duplicate_grouping_threshold_last_price) and (slope_angle_diff < duplicate_grouping_threshold_slope)) \
          and (i_is_breakout == j_is_breakout):
        best_matching_idx = j
        break

    if(best_matching_idx != -1):
      this_row = row_i
      best_matching_row = trends_df.iloc[best_matching_idx]

      this_row_group = this_row['duplicate_group_id']
      best_matching_row_group = best_matching_row['duplicate_group_id']

      group_id_for_pair = best_matching_row_group if best_matching_row_group is not None else group_idx

      if best_matching_row_group == None:
        trends_df.loc[best_matching_row.name, 'duplicate_group_id'] = group_id_for_pair

      if this_row_group == None:
        trends_df.loc[this_row.name, 'duplicate_group_id'] = group_id_for_pair
      else:
        for k in range(0, len(trends_df)):
          row_k = trends_df.iloc[k]
          if row_k['duplicate_group_id'] == this_row_group:
            trends_df.loc[row_k.name, 'duplicate_group_id'] = group_id_for_pair

    else:
      trends_df.loc[row_i.name, 'duplicate_group_id'] = group_idx
    group_idx += 1
  
  # For all the duplicate groups found, mark best for each group
  if(len(trends_df) == 1):
    trends_df.loc[ trends_df.iloc[0].name , 'is_best_from_duplicate_group'] = True
    trends_df.loc[ trends_df.iloc[0].name , 'overall_rank'] = 1
    trends_df.loc[ trends_df.iloc[0].name, 'rank_within_group'] = 1
    return

  best_results = trends_df.sort_values(by='score', ascending=True).groupby(["duplicate_group_id"]).last().reset_index()
  overall_rank = 1

  for i in range(0, len(best_results)):
    row = best_results.iloc[i]
    trends_df.loc[ trends_df['id'] == row['id'] , 'is_best_from_duplicate_group'] = True
    trends_df.loc[ trends_df['id'] == row['id'] , 'overall_rank'] = overall_rank
    overall_rank += 1

  # Mark rank within each group
  dup_groups = trends_df.groupby(["duplicate_group_id"])
  for group_name, df_group in dup_groups:
    group_rank = 1

    df_group_sorted = df_group.sort_values(by='score', ascending=False)

    for row_index, row in df_group_sorted.iterrows():
      trends_df.loc[row_index, 'rank_within_group'] = int(group_rank)
      group_rank += 1

  return trends_df