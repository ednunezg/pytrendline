import os

# Core lib
import pandas as pd
from dataclasses import dataclass


# Lib imports
from pytrendline import structs, detect, plot
from fixtures import testcases

@dataclass
class ResultAssert:
  trendline_asserts: list
  number_of_groups: int = 0

@dataclass
class TrendlineAssert:
  trend_type: str
  trend_id: str
  is_breakout: bool
  breakout_index: int = 0
  overall_rank: int = 1
  rank_within_group: int = 1



def test_findtrends():
  tests = [
    {
      "name": "Multiple R+S breakouts trendline found [breakouts enabled]",
      "candles": testcases.NO_TREND_DUE_BREAKOUT_5m,
      "time_interval": '5m',
      "result_assert": ResultAssert(
        [
          TrendlineAssert("SUPPORT", "S-[0,1,2,3,4]", True, 5, 1, 1),
          TrendlineAssert("SUPPORT", "S-[1,2,3,4]", True, 5, None, 2),
          TrendlineAssert("SUPPORT", "S-[2,3,4]", True, 5, None, 3),
          TrendlineAssert("RESISTANCE", "R-[0,1,2,3,4]", True, 5, 1, 1),
          TrendlineAssert("RESISTANCE", "R-[1,2,3,4]", True, 5, None, 2),
          TrendlineAssert("RESISTANCE", "R-[2,3,4]", True, 5, None, 3),
        ], 2
      ),
      "breakout_enabled": True,
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "No trendline found despite breakout [breakouts disabled]",
      "candles": testcases.NO_TREND_DUE_BREAKOUT_5m,
      "time_interval": '5m',
      "result_assert": ResultAssert(
        [], 0
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "No trendline found 5m",
      "candles": testcases.NO_TREND_5m,
      "time_interval": '5m',
      "result_assert": ResultAssert(
        [], 0
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "No trendline found 1d",
      "candles": testcases.NO_TREND_1d,
      "time_interval": '1d',
      "result_assert": ResultAssert(
        [], 0
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "Support line with 6pts 5m",
      "candles": testcases.SUP_6pt_TREND_5m,
      "time_interval": '5m',
      "result_assert": ResultAssert(
        [
          TrendlineAssert("SUPPORT", "S-[0,1,2,3,4,5]", False, 0, 1, 1),
        ], 1
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "Support line with 6pts 1d",
      "candles": testcases.SUP_6pt_TREND_1d,
      "time_interval": '1d',
      "result_assert": ResultAssert(
        [
          TrendlineAssert("SUPPORT", "S-[0,1,2,3,4,5]", False, 0, 1, 1),
        ], 1
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "Resistance line with 6pts 1d",
      "candles": testcases.RES_6pt_TREND_1d,
      "time_interval": '1d',
      "result_assert": ResultAssert(
        [
          TrendlineAssert("RESISTANCE", "R-[0,1,2,3,4,5]", False, 0, 1, 1),
        ], 1
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "Support line with 3pts 1d",
      "candles": testcases.SUP_3pt_TREND_1d,
      "time_interval": '1d',
      "result_assert": ResultAssert(
        [
          TrendlineAssert("SUPPORT", "S-[2,3,4]", False, 0, 1, 1),
        ], 1
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "Two support lines and one resistance line",
      "candles": testcases.TWO_SUP_AND_ONE_RES_TREND_1d,
      "time_interval": '1d',

      "result_assert": ResultAssert(
        [
          TrendlineAssert("RESISTANCE", "R-[0,1,2,3,4,5,6]", False, 0, 1, 1),
          TrendlineAssert("SUPPORT", "S-[0,1,2]", False, 0, 1, 1),
          TrendlineAssert("SUPPORT", "S-[4,5,6]", False, 0, 2, 1),
        ], 3
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "One flat support and one flat resistance",
      "candles": testcases.FLAT_RES_AND_SUP,
      "time_interval": '1d',
      "result_assert": ResultAssert(
        [
          TrendlineAssert("SUPPORT", "S-[1,2,4]", False, 0, 1, 1),
          TrendlineAssert("RESISTANCE", "R-[1,3,5]", False, 0, 1, 1),
        ], 2
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "One res line with global max/min pt, search globals only",
      "candles": testcases.ONE_RES_LINE_WITH_GLOBAL_MAX_1d,
      "time_interval": '1d',
      "search_global_max_min_only": True,
      "result_assert": ResultAssert(
        [
          TrendlineAssert("RESISTANCE", "R-[2,3,4]", False, 0, 1, 1),
        ], 1
      ),
      "expect_err": False,
      "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "One res line with global max/min pt, search all",
      "candles": testcases.ONE_RES_LINE_WITH_GLOBAL_MAX_1d,
      "time_interval": '1d',
      "search_global_max_min_only": False,
      "result_assert": ResultAssert(
        [
          TrendlineAssert("RESISTANCE", "R-[2,3,4]", False, 0, 1, 1),
        ], 1
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "One res line without global max/min pt, search globals only",
      "candles": testcases.ONE_RES_LINE_WITHOUT_GLOBAL_MAX_1d,
      "time_interval": '1d',
      "search_global_max_min_only": True,
      "result_assert": ResultAssert(
        [], 0
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "One res line without global max/min pt, search all",
      "candles": testcases.ONE_RES_LINE_WITHOUT_GLOBAL_MAX_1d,
      "time_interval": '1d',
      "search_global_max_min_only": False,
      "result_assert": ResultAssert(
        [
          TrendlineAssert("RESISTANCE", "R-[2,3,4]", False, 0, 1, 1),
        ], 1
      ),
      "expect_err": False,
      # "open_plot": True # Uncomment to see bokeh result in browser
    },
  ]

  for test in tests:
    print("Running test '" + test['name'] + "'")

    results = detect(
      candlestick_data=test["candles"],
      trend_type=structs.TrendlineTypes.BOTH,
      first_pt_must_be_pivot=False,
      last_pt_must_be_pivot=False,
      all_pts_must_be_pivots=False,
      trendline_must_include_global_maxmin_pt=test.get("search_global_max_min_only", False),
      min_points_required=3,
      scan_from_date=None,
      ignore_breakouts=not test.get("breakout_enabled", False),
      config={
        # Force the tolerance to be very small as to make expected test case results sclear cut
        "max_allowable_error_pt_to_trend": lambda candles: 0.10,
        "duplicate_grouping_threshold_last_price": lambda candles: 0.40,
      }
    )      

    asserts = test["result_assert"]
    all_results_df = pd.concat([results['support_trendlines'], results['resistance_trendlines']])
    num_groups = len(all_results_df.groupby(["duplicate_group_id", "trendtype"]))
  
    if test.get("open_plot", False):
      outf = plot(
        results=results,
        filedir='.',
        filename='test_output.html',
      )
      os.system("open " + outf)

    # Check number of groups and number of trendlines ok
    assert num_groups == asserts.number_of_groups, "Expected number of groups in result to be {}, received {}".format(asserts.number_of_groups, num_groups)

    # Check individual trendlines
    for trend in asserts.trendline_asserts:
      '''
      assert:
        trend id
        trend type
        is breakout
        breakout at index
        overall rank
        rank within group
      '''
      trends_w_id = all_results_df.loc[all_results_df['id'] == trend.trend_id]
      assert len(trends_w_id) == 1, "Expected trend with id {} to exist".format(trend.trend_id)

      result_trend = trends_w_id.iloc[0]

      assert result_trend["trendtype"] == trend.trend_type, "Expected trend with id {} to have trend type '{}', received '{}'".format(trend.trend_id, trend.trend_type, result_trend["trendtype"])
      assert result_trend["is_breakout"] == trend.is_breakout, "Expected trend with id {} to have is_breakout={}".format(trend.trend_id, trend.is_breakout)
      if trend.is_breakout: assert result_trend["breakout_index"] == trend.breakout_index, "Expected trend with id {} to have breakout index at {}".format(trend.trend_id, trend.breakout_index)
      assert result_trend["overall_rank"] == trend.overall_rank, "Expected trend with id {} to have overall_rank of {}, received {}".format(trend.trend_id, trend.overall_rank, result_trend["overall_rank"])
      assert result_trend["rank_within_group"] == trend.rank_within_group, "Expected trend with id {} to have rank_within_group of {}".format(trend.trend_id, trend.rank_within_group)
