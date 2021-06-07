# Insert project root in order to allow library imports in root
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import importlib
import pytest
import mock
from unittest.mock import Mock
from unittest.mock import MagicMock

# Test fixtures
from fixtures import candlesticks

# Libs
from lib import stock_data
from lib import plotting
from lib import util
from lib import config

GEN_BOKEH_STASH = plotting.gen_bokeh
OPEN_FILE_STASH = util.open_file

def noop_fn(*args, **kwargs):
  return

def setup():
  # Don't allow stock data to be pulled from cache
  config.ALLOW_STOCK_DATA_DATASETS = False
  prevent_bokeh_gen_and_open()
  
def prevent_bokeh_gen_and_open():
  # Prevent generating bokeh and opening up file
  plotting.gen_bokeh = MagicMock(side_effect=noop_fn)
  util.open_file = MagicMock(side_effect=noop_fn)

def reset_bokeh_gen_and_open():
  # Prevent generating bokeh and opening up file
  plotting.gen_bokeh = GEN_BOKEH_STASH
  util.open_file = OPEN_FILE_STASH

# --------------------------

def async_return(result):
  async_fn = asyncio.Future()
  async_fn.set_result(result)
  return async_fn

def mock_fetch_stockdata(df):
  stock_data_class = stock_data.StockData
  stock_data_class._fetch_ameritrade = MagicMock(return_value=async_return(df))

# --------------------------

def test_findtrends(script_runner):
  tests = [
    {
      "name": "No trendline found due to breakout 5m",
      "candles": candlesticks.NO_TREND_DUE_BREAKOUT_5m,
      "time_interval": '5m',
      "assert_outputs": [
        "0 Resistance trendlines found",
        "0 Support trendlines found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "No trendline found 5m",
      "candles": candlesticks.NO_TREND_5m,
      "time_interval": '5m',
      "assert_outputs": [
        "0 Resistance trendlines found",
        "0 Support trendlines found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "No trendline found 1d",
      "candles": candlesticks.NO_TREND_1d,
      "time_interval": '1d',
      "assert_outputs": [
        "0 Resistance trendlines found",
        "0 Support trendlines found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "Support line with 6pts 5m",
      "candles": candlesticks.SUP_6pt_TREND_5m,
      "time_interval": '5m',
      "assert_outputs": [
        "0 Resistance trendlines found",
        "1 Support trendlines found",
        "6pt Support line with uuid S-[0,1,2,3,4,5] found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "Support line with 6pts 1d",
      "candles": candlesticks.SUP_6pt_TREND_1d,
      "time_interval": '1d',
      "assert_outputs": [
        "0 Resistance trendlines found",
        "1 Support trendlines found",
        "6pt Support line with uuid S-[0,1,2,3,4,5] found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "Resistance line with 6pts 1d",
      "candles": candlesticks.RES_6pt_TREND_1d,
      "time_interval": '1d',
      "assert_outputs": [
        "1 Resistance trendlines found",
        "0 Support trendlines found",
        "6pt Resistance line with uuid R-[0,1,2,3,4,5] found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "Support line with 3pts 1d",
      "candles": candlesticks.SUP_3pt_TREND_1d,
      "time_interval": '1d',
      "assert_outputs": [
        "0 Resistance trendlines found",
        "1 Support trendlines found",
        "3pt Support line with uuid S-[2,3,4] found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "Support line within first three indices",
      "candles": candlesticks.ONE_SUP_TREND_IN_FIRST_THREE_INDECES,
      "time_interval": '1d',
      "assert_outputs": [
        "0 Resistance trendlines found",
        "1 Support trendlines found",
        "3pt Support line with uuid S-[0,1,2] found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "Two support lines and one resistance line",
      "candles": candlesticks.TWO_SUP_AND_ONE_RES_TREND_1d,
      "time_interval": '1d',
      "assert_outputs": [
        "1 Resistance trendlines found",
        "2 Support trendlines found",
        "3pt Support line with uuid S-[0,1,2] found",
        "3pt Support line with uuid S-[4,5,6] found",
        "7pt Resistance line with uuid R-[0,1,2,3,4,5,6] found",
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "One flat support and one flat resistance",
      "candles": candlesticks.FLAT_RES_AND_SUP,
      "time_interval": '1d',
      "assert_outputs": [
        "1 Resistance trendlines found",
        "1 Support trendlines found",
        "6pt Support line with uuid S-[0,1,2,3,4,5] found",
        "6pt Resistance line with uuid R-[0,1,2,3,4,5] found",
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "One res line with global max/min pt, search globals only",
      "candles": candlesticks.ONE_RES_LINE_WITH_GLOBAL_MAX_1d,
      "time_interval": '1d',
      "search_global_max_min_only": True,
      "assert_outputs": [
        "1 Resistance trendlines found",
        "0 Support trendlines found",
        "3pt Resistance line with uuid R-[0,3,4] found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "One res line with global max/min pt, search all",
      "candles": candlesticks.ONE_RES_LINE_WITH_GLOBAL_MAX_1d,
      "time_interval": '1d',
      "search_global_max_min_only": False,
      "assert_outputs": [
        "1 Resistance trendlines found",
        "0 Support trendlines found",
        "3pt Resistance line with uuid R-[0,3,4] found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "One res line without global max/min pt, search globals only",
      "candles": candlesticks.ONE_RES_LINE_WITHOUT_GLOBAL_MAX_1d,
      "time_interval": '1d',
      "search_global_max_min_only": True,
      "assert_outputs": [
        "0 Resistance trendlines found",
        "0 Support trendlines found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
    {
      "name": "One res line without global max/min pt, search all",
      "candles": candlesticks.ONE_RES_LINE_WITHOUT_GLOBAL_MAX_1d,
      "time_interval": '1d',
      "search_global_max_min_only": False,
      "assert_outputs": [
        "1 Resistance trendlines found",
        "0 Support trendlines found",
        "3pt Resistance line with uuid R-[2,3,4] found"
      ],
      "expect_err": False,
      # "open_bokeh": True # Uncomment to see bokeh result in browser
    },
  ]


  setup()
  for test in tests:
    print("Running test '" + test['name'] + "'")

    # Mocks
    if test.get("open_bokeh", False):
      reset_bokeh_gen_and_open()
    else:
      prevent_bokeh_gen_and_open()
    mock_fetch_stockdata(test["candles"])

    # Run the script
    if test.get("search_global_max_min_only", False):
      ret = script_runner.run('findtrends.py', 'AAPL', '-t', test["time_interval"], "-globalmaxmin")
    else:
      ret = script_runner.run('findtrends.py', 'AAPL', '-t', test["time_interval"])

    # Check the program crashed with err or not
    if test["expect_err"]:
      assert len(ret.stderr) > 0, "Expected an error for " + test["name"]
    else:
      assert len(ret.stderr) == 0, "Expected no error for " + test["name"]

    # Check that we have the right prints to console
    if "assert_outputs" in test and len(test["assert_outputs"]) > 0:
      for output in test["assert_outputs"]:
        assert output in ret.stdout, "Expected output '" + output + "' for test w name '" + test["name"] + "'"