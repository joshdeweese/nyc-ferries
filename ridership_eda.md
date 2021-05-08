---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.2
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
from  scipy.stats import zscore
import plotly.io as pio
import plotly

pd.set_option('display.max_rows', 500)
```

```python pycharm={"name": "#%%\n"}
df = pd.read_csv('data/final.csv')
```

```python
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp()
df['DateSTR'] = df['Date'].astype(str)
```

```python
# Group some of the companies because they have very little activity, or were consolodated.
df['Operator'] = np.where(df['Company'] == 'Billy Bey', 'NY Waterway', df['Company'])
df['Operator'] = np.where(df['Operator'].str.contains('NY Waterway'), 'NY Waterway', df['Operator'])
df['Operator'] = np.where(df['Operator'] == 'Water Tours', 'Other', df['Operator'])
df['Operator'] = np.where(df['Operator'] == 'HMS', 'Other', df['Operator'])
df['Operator'] = np.where(df['Operator'] == 'Baseball', 'Other', df['Operator'])
```

```python
df['z_score'] = df.groupby('Operator')['Rides'].transform(lambda x: zscore(x))
```

```python pycharm={"name": "#%%\n"}
plotly.offline.init_notebook_mode(connected=True)
df_plot = df[['Operator', 'Company', 'Date', 'DateSTR', 'Rides']]

fig = px.scatter(df_plot, x="Date", y="Rides", color="Company", facet_col="Operator", 
                 facet_col_wrap=3, custom_data=['DateSTR'])
fig.update_yaxes(matches=None)
fig.update_traces(
    hovertemplate="<br>".join([
        "Date: %{customdata[0]}",
        "Rides: %{y}",
    ])
)
fig.show()
```

```python
df_plot = df[df['z_score'] <= 3]
df_plot = df_plot.groupby(['Operator', 'Company', 'Date', 'DateSTR']).agg({'Rides':'sum'}).reset_index()



fig = px.scatter(df_plot, x="Date", y="Rides", color="Company", facet_col="Operator", 
                 facet_col_wrap=3, custom_data=['DateSTR'])
fig.update_yaxes(matches=None)
fig.update_traces(
    hovertemplate="<br>".join([
        "Date: %{customdata[0]}",
        "Rides: %{y}",
    ])
)
fig.show()
```

```python
df = df[df['z_score'] <= 3]
```

```python
df_grouped = df.groupby(['Operator', 'Date', 'DateSTR', 'Weekend']).agg({'Rides':'sum'}).reset_index()

fig = px.scatter(df_grouped, x="Date", y="Rides", facet_col="Operator", color='Weekend',
                 facet_col_wrap=3, custom_data=['DateSTR'])
#fig.update_yaxes(matches=None)
fig.update_traces(
    hovertemplate="<br>".join([
        "Date: %{customdata[0]}",
        "Rides: %{y}",
    ])
)
fig.show()
```

```python
df_grouped = df.groupby(['Date', 'DateSTR', 'Day', 'Weekend']).agg({'Rides':'sum'}).reset_index()


fig = px.scatter(df_grouped, x="Date", y="Rides", color='Weekend', custom_data=['DateSTR'])
fig.update_yaxes(matches=None)
fig.update_traces(
    hovertemplate="<br>".join([
        "Date: %{customdata[0]}",
        "Rides: %{y}",
    ])
)
fig.show()
```

```python
fig = px.histogram(df, x='z_score', nbins=15)
fig.show()
```

```python
fig = px.histogram(df, x="Rides", nbins=20)
fig.update_traces(xbins=dict( # bins used for histogram
        start=0.0,
        end=6000.0
    ))
fig.show()
```

```python
df.groupby('Operator')['Rides'].describe()
```

```python
df['Rides'].describe()
```

```python
grouped = df.groupby('Day')['Rides'].sum()
#grouped_sorted = grouped.sort_values('Rides', ascending=True).reset_index()


fig = px.bar(grouped)
fig.update_layout(xaxis={'categoryorder':'total descending'})
fig.show()
```

```python
weather = pd.read_csv('data/open_weather_map_data.csv')
```

```python
weather.columns
```

```python
weather['date'] = weather['dt_iso'].str[:10]
```

```python
grouped_weather = weather.groupby('date').agg({'temp': 'mean', 'feels_like': 'mean', 'temp_min': 'min',
                                              'temp_max': 'max', 'humidity': 'mean', 'rain_1h': 'sum', 'snow_1h': 'sum',
                                              'clouds_all': 'mean'}).reset_index()

# Convert measurments fro mm to inches
grouped_weather['rain_1h'] = grouped_weather['rain_1h'] * 0.0393701
grouped_weather['snow_1h'] = grouped_weather['snow_1h'] * 0.0393701


grouped_weather.columns = ['date', 'temp_avg', 'feels_like_avg', 'temp_min', 'temp_max', 'humidity_avg', 'rain_in',
                          'snow_in', 'cloud_pct_avg']
grouped_weather
```

```python
grouped_ridership = df[['DateSTR', 'Rides']].groupby('DateSTR').sum()
daily_ridership_weather = grouped_ridership.merge(grouped_weather, how='left', left_on='DateSTR', right_on='date')
```

```python
#ridership_subset = daily_ridership_weather[daily_ridership_weather['date'].str[:4] == '2020']
ridership_subset = daily_ridership_weather

fig = px.line(ridership_subset, x='date', y=['Rides'])
fig2 = px.line(ridership_subset, x='date', y=['temp_avg'])

subfig = make_subplots(specs=[[{"secondary_y": True}]])

fig2.update_traces(yaxis="y2")
subfig.add_traces(fig.data + fig2.data)

subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
pio.write_html(subfig, file="index.html", auto_open=True)
subfig.show()
```

```python

```
