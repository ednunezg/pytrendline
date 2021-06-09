import os
import pandas as pd
import numpy as np

from bokeh.resources import CDN
from bokeh.models.widgets import Div
from bokeh.plotting import figure
from bokeh.models import Label
from bokeh.embed import file_html

from datetime import timedelta
from colour import Color

from math import pi, tan

from . import structs

css_hack = '''
.dataframe {
	border: 1px solid grey;
	border-collapse: separate;
	border-spacing: 15px 5px;
	white-space: nowrap;
}

/* SECTION SHOWING LOG HISTORY */
details {
  background: white;
  border: 1px solid grey;
  color: #333333;
  border-radius: 4px;
  overflow-x: scroll;
  margin-top: 30px;
  margin-bottom: 30px;
  max-width: fit-content;
}

details summary {
  font-family: Courier;
  font-size: 16px;
  display: block;
  cursor: pointer;
  padding-right: 10px;
  padding-left: 10px;
  padding-top: 5px;
  padding-bottom: 5px;
  color: #2b2b2b;

}

details:not([open]) summary:hover,
details:not([open]) summary:focus {      
  background: #ffffff;
  color: #454545;
}

details[open] summary {
  border: 1px solid #003eff;
}

details main {
  padding: 0em;
  font-family: Courier;
  font-size: 14px;
}
'''

class TrendlineFigure():
  # point_set can either be a slice of date strings or a slice of indices

  def __init__(self, trend_type, result_row, plotting_prop_overrides = {}):
    self.type = trend_type

    self.id = result_row['id']
    self.pointset_dates = result_row['pointset_dates']
    self.breakout_index = result_row['breakout_index']
    self.is_breakout = result_row['is_breakout']
    self.score = result_row['score']
    self.includes_global_max_or_min = result_row['includes_global_max_or_min']
    self.global_maxs_or_mins = result_row['global_maxs_or_mins']
    self.is_best_from_duplicate_group = result_row['is_best_from_duplicate_group']
    self.plotting_prop_overrides = plotting_prop_overrides

  def plot_figure(self, p, candles_df, opts={}):    
    pointset_indeces = []
    for date in self.pointset_dates:
      pointset_indeces.append( candles_df.loc[candles_df['Date'] == date].index[0] )

    pt_set_y = []
    pt_set_x = pointset_indeces

    for pt in pt_set_x:
      if self.type == structs.TrendlineTypes.RESISTANCE:
        pt_set_y.append(candles_df.iloc[pt].High)
      elif self.type == structs.TrendlineTypes.SUPPORT:
        pt_set_y.append(candles_df.iloc[pt].Low)
      else:
        pt_set_y.append(candles_df.iloc[pt].Low)

    # Calculate slope and intersect using first point and last point
    m, b = np.polyfit([pt_set_x[0], pt_set_x[-1]], [pt_set_y[0], pt_set_y[-1]], 1)

    if self.is_breakout:
      last_date_index = self.breakout_index + 0.05
      last_date_trendline_price = m * last_date_index + b
      p.x([last_date_index], [last_date_trendline_price], line_width=3, size=10, color="red", alpha=0.8)
    else:
      last_date_index = len(candles_df) - 1

    tl_vals_at_x = pt_set_y
    tl_y_at_last_date = m * last_date_index + b

    color = self.get_trendline_plot_color()

    p.segment(
      x0=[pt_set_x[0]],
      y0=[tl_vals_at_x[0]],
      x1=[last_date_index],
      y1=[tl_y_at_last_date],
      color=color,
      line_width=self.get_trendline_plot_line_width(),
      line_dash=self.get_trendline_plot_line_style()
    )

    # Draw plot score label
    if self.is_best_from_duplicate_group:
      label_text =  "Score " + str(self.id) + " = " + str(round(self.score, 2))
      if self.is_breakout: label_text += " (breakout at {})".format(self.breakout_index)
      
      label_x_pos = last_date_index + 2
      label_y_pos = tl_y_at_last_date + (2 * m)

      label = Label(x=label_x_pos, y=label_y_pos,
                 text=label_text, render_mode='css',
                 border_line_color=color, border_line_alpha=0.8,
                 background_fill_color='white', background_fill_alpha=1.0)
      p.segment(
        x0=[last_date_index],
        y0=[tl_y_at_last_date],
        x1=[last_date_index + 2],
        y1=[tl_y_at_last_date + (m * 2)],
        color=color,
        line_width=self.get_trendline_plot_line_width(),
        line_dash=self.get_trendline_plot_line_style()
      )
      p.add_layout(label)

    # Mark points that make up trendline
    p.square(pt_set_x, tl_vals_at_x, size=12, color=color, alpha=0.5)

    # Mark global maxs or mins
    for date in self.global_maxs_or_mins:
      query = candles_df.loc[candles_df['Date'] == date]
      if len(query) == 0: continue
      index = query.iloc[0].name

      if self.type == structs.TrendlineTypes.RESISTANCE:
        price = candles_df.iloc[index].High
      elif self.type == structs.TrendlineTypes.SUPPORT:
        price = candles_df.iloc[index].Low
      p.circle(index, price, size=20, color="gold", alpha=0.3)

  def get_trendtype_string(self):
    if self.type == structs.TrendlineTypes.RESISTANCE:
      return "Resistance"
    elif self.type == structs.TrendlineTypes.SUPPORT:
      return "Support"
    else:
      return "Unknown"

  def get_trendline_plot_color(self):
    # If we have set an override for plot color, use this
    if "color" in self.plotting_prop_overrides:
      return self.plotting_prop_overrides["color"]

    orange = Color("darkorange")
    purple = Color("steelblue")
    grey = Color("slategrey")

    if self.type == structs.TrendlineTypes.SUPPORT:
      c = purple
    else:
      c = orange
    
    if self.is_breakout:
      # Set color to grey if we find that line has expired
      c = grey

    
    return c.hex_l

  def get_trendline_plot_line_width(self):
    if "line_width" in self.plotting_prop_overrides:
      return self.plotting_prop_overrides["line_width"]

    if self.is_breakout:
      return 1
    
    else:
      if self.is_best_from_duplicate_group:
        return 2
      else:
        return 1

  def get_trendline_plot_line_style(self):
    if "line_style" in self.plotting_prop_overrides:
      return self.plotting_prop_overrides["line_style"]

    if self.is_breakout:
      return "dotted"
    elif self.is_best_from_duplicate_group:
      return "dashed"
    else:
      return "dotted"

def _draw_bidirectional_ray(p, x, y, angle, color, width=2, dash="dashed"):
  p.segment(x0=x, x1=x, y0=0, y1=10000, line_color=color, line_dash=dash, line_width=width)

def _highlight_pivots(p, pivots_indexes, col, candles_df):
  # Highlight pivot points
  pivots_x_vals = []
  pivots_y_vals = []
  for pivot_idx in pivots_indexes:
    pivot_panda_ts = candles_df.iloc[pivot_idx].name
    pivot_y_val = candles_df.iloc[pivot_idx][col]
    pivots_x_vals.append(pivot_panda_ts)
    pivots_y_vals.append(pivot_y_val)
  p.diamond(pivots_x_vals, pivots_y_vals, size=20, line_color="green", fill_alpha=0.1, alpha=0.5)

def plot_graph_bokeh(results):
  candlestick_data = results["candlestick_data"]

  # Plot
  candles_df = candlestick_data.df

  site_title = '{} trendlines for {}m candlesticks'.format(
    "RESISTANCE and SUPPORT" if results["trend_type"] == "BOTH" else results["trend_type"],
    candlestick_data.time_interval_min(),
  )
  
  
  # Establish plot dimensions
  y_padding = (candles_df['High'].max() / 200)
  y_range_top = candles_df['Low'].min() - y_padding
  y_range_bottom = candles_df['High'].max() + y_padding
  x_range_left = -1
  x_range_right = len(candles_df) + 10
  
  
  # Plot candlestick chart
  inc = candles_df.Close > candles_df.Open
  dec = candles_df.Open > candles_df.Close
  w = 0.5

  p = figure(
    x_axis_type="datetime",
    tools="pan,wheel_zoom,tap,crosshair,hover,poly_draw,reset,save",
    plot_width=1300,
    title=site_title,
    y_range=(y_range_top, y_range_bottom),
    x_range=(x_range_left, x_range_right),
  )
  
  p.xaxis.major_label_overrides = {
    i: date.strftime('%b %d %H:%M') for i, date in enumerate(candles_df['Date'])
  }

  p.xaxis.major_label_orientation = pi/4
  p.grid.grid_line_alpha=0.3
  p.segment(candles_df.index, candles_df.High, candles_df.index, candles_df.Low, color="black")
  p.vbar(candles_df.index[inc], w, candles_df.Open[inc], candles_df.Close[inc], fill_color="#D5E1DD", line_color="black")
  p.vbar(candles_df.index[dec], w, candles_df.Open[dec], candles_df.Close[dec], fill_color="#F2583E", line_color="black")

  # Plot trendlines (support)
  if 'support_trendlines' in results:
    for _, result_row in results['support_trendlines'].iterrows():
      tf = TrendlineFigure(structs.TrendlineTypes.SUPPORT, result_row)
      tf.plot_figure(p, candles_df)

  # Plot trendlines (resistsance)
  if 'resistance_trendlines' in results:
    for _, result_row in results['resistance_trendlines'].iterrows():
      tf = TrendlineFigure(structs.TrendlineTypes.RESISTANCE, result_row)
      tf.plot_figure(p, candles_df)

  # Draw vertical lines at first and last price
  _draw_bidirectional_ray(p, candles_df.index[0] - 0.5, 0, 90, "#bbbbbb")
  _draw_bidirectional_ray(p, candles_df.index[-1] + 0.5, 0, 90, "#bbbbbb")


  # Highlight pivot points
  if 'support_pivots' in results:
    _highlight_pivots(p, results['support_pivots'], "Low", candles_df)
  if 'resistance_pivots' in results:
    _highlight_pivots(p, results['resistance_pivots'], "High", candles_df)

  # Styling nits
  p.title.text_font_size = '16pt'

  return p

def plot_table_bokeh(results):
  if results['trend_type'] == structs.TrendlineTypes.BOTH:
    all_results = pd.concat([results['support_trendlines'], results['resistance_trendlines']])
  elif results['trend_type'] == structs.TrendlineTypes.SUPPORT:
    all_results = results['support_trendlines']
  else:
    all_results = results['resistance_trendlines']

  if len(all_results) > 0:
    html_trends_table = all_results.drop('pointset_dates', 1).to_html(border=0, header=True, index=False, justify="left", float_format=lambda x: '%10.3f' % x)
  else:
    html_trends_table = '<p>No trendlines found</p>'

  div = Div(text="", width=1000)
  div.text = '''
    <div>
      <h1>Trendline results:</h1><br/>
      {}
    </div>
  '''.format(html_trends_table)

  return div

def plot(
  results=None,
  filedir='.',
  filename='trend_plot.html',
):
  # Validate data
  if results == None or type(results) != dict:
    raise Exception("results argument for plot needs to be output of detect(...)")

  # Plot candlestick graph with trendlines
  trend_graph = plot_graph_bokeh(results)

  # Plot trendline results dataframe below the plot
  trend_table = plot_table_bokeh(results)

  # Get HTML content
  filepath = filedir + '/' + filename
  html_content = file_html(models=(trend_graph, trend_table), resources=(CDN), title="pytrendline results")

  # Hack in extra styles to HTML
  html_content = html_content.replace('<head>', '<head><style class="custom" type="text/css">{}</style>'.format(css_hack))

  # Write HTML to file
  with open(filepath, 'w') as outfile:
    outfile.write(html_content)
  
  return filepath