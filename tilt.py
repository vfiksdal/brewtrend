#!/usr/bin/env python3
#
# Show demodulator output in real-time
#

from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.graph_objects as go
import requests,json,time
import numpy as np
from dash.dependencies import Input, Output
from datetime import datetime
from webapp import app
from dash.exceptions import PreventUpdate

def layout(name):
    # Collect timing information
    t_interval=app.historian.interval
    if t_interval<10: t_interval=10
    if app.historian.fahrenheit:
        tunit='Fahrenheit'
    else:
        tunit='Celsius'

    # Define UI
    container=[]
    container.append(dbc.Row([dbc.Col(html.H1(id='runtime'))]))
    container.append(dcc.Interval(id='tilt_interval',interval=t_interval*1000,n_intervals=0))
    container.append(dbc.Row([
        dbc.Col(daq.Gauge(id='tilt_gauge_gravity',
                color={"gradient":True,"ranges":{"green":[0.9,1.005],"yellow":[1.005,1.020],"red":[1.020,1.100]}},
                min=0.900,max=1.100,showCurrentValue=True,units='SG',label='Specific Gravity')),
        dbc.Col(daq.Gauge(id='tilt_gauge_temperature',
                color={"gradient":True,"ranges":{"green":[0,20],"yellow":[20,25],"red":[25,30]}},
                min=0,max=30,showCurrentValue=True,units=tunit,label='Temperature'))
    ]))
    container.append(dbc.Row(dbc.Col(dcc.Graph(id='tilt_plot_gravity'))))
    container.append(dbc.Row(dbc.Col(dcc.Graph(id='tilt_plot_temperature'))))
    return html.Div([dbc.Container(container)])


@app.callback(
        Output('tilt_gauge_gravity','value'),
        Output('tilt_gauge_temperature','value'),
        Output('tilt_plot_gravity','figure'),
        Output('tilt_plot_temperature','figure'),
        Input('tilt_interval','n_intervals'),
        Input('cache','children'))
def update_graph_per_bit(n,cache):
    if len(cache)==0 or not cache in app.historian.data:
        raise PreventUpdate

    data=app.historian.data[cache]
    t=[]
    sg=[]
    tt=[]
    for i in range(0,len(data)):
        t.append(datetime.fromtimestamp(data[i].time))
        sg.append(data[i].gravity)
        tt.append(data[i].temperature)
    if app.historian.fahrenheit:
        tunit='Fahrenheit'
    else:
        tunit='Celsius'

    # Update plots
    gfig=go.Figure(data=[go.Scatter(x=t,y=sg,mode='lines+markers',marker=dict(color='Red'))])
    gfig.update_layout(title='Specific Gravity',yaxis_title='Oechsle',xaxis_title='Time',template="plotly_dark",title_x=0.5,uirevision=True)
    tfig=go.Figure(data=[go.Scatter(x=t,y=tt,mode='lines+markers',marker=dict(color='Red'))])
    tfig.update_layout(title='Temperature',yaxis_title=tunit,xaxis_title='Time',template="plotly_dark",title_x=0.5,uirevision=True)

    return sg[-1],tt[-1],gfig,tfig


