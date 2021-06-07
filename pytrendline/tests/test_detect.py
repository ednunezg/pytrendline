from .. import structs, detect, plot
from ../fixtures import tests.py

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