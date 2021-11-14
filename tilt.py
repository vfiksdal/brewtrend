#!/usr/bin/env python3
#
# Show demodulator output in real-time
#

from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.graph_objects as go
import time
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
        Input('datepicker','start_date'),
        Input('datepicker','end_date'),
        Input('cache','children'))
def update_tilt(n,start,end,cache):
    # Block bullshit requests
    if len(cache)==0 or not cache in app.historian.data:
        raise PreventUpdate

    # Collect requested data
    t=[]
    sg=[]
    tt=[]
    data=app.historian.data[cache]
    _start=0
    _end=0
    if start:   _start=time.mktime(time.strptime(start,'%Y-%m-%d'))
    if end:     _end=time.mktime(time.strptime(end,'%Y-%m-%d'))
    for i in range(0,len(data)):
        if data[i].time>_start and (_end==0 or data[i].time<_end):
            t.append(datetime.fromtimestamp(data[i].time))
            sg.append(data[i].gravity)
            tt.append(data[i].temperature)

    # Update plots
    if app.historian.fahrenheit:
        tunit='Fahrenheit'
    else:
        tunit='Celsius'
    gfig=go.Figure(data=[go.Scatter(x=t,y=sg,mode='lines+markers',marker=dict(color='Red'))])
    gfig.update_layout(title='Specific Gravity',yaxis_title='Oechsle',xaxis_title='Time',template="plotly_dark",title_x=0.5,uirevision=True)
    tfig=go.Figure(data=[go.Scatter(x=t,y=tt,mode='lines+markers',marker=dict(color='Red'))])
    tfig.update_layout(title='Temperature',yaxis_title=tunit,xaxis_title='Time',template="plotly_dark",title_x=0.5,uirevision=True)
    _sg=0
    _tt=0
    if len(t):
        _sg=sg[-1]
        _tt=tt[-1]
    
    return _sg,_tt,gfig,tfig

