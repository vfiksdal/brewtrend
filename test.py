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

def layout(device,color,batch):
    container=[]
    container.append(dbc.Row([dbc.Col(html.H1(children=device))]))
    container.append(dbc.Row([dbc.Col(html.H1(children=color))]))
    container.append(dbc.Row([dbc.Col(html.H1(children=batch))]))
    return html.Div([dbc.Container(container)])


