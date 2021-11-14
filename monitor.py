#!/usr/bin/env python3
#
# Entry point for web application
#

# Import system modules
from dash import dcc
from dash import html
from flask import request
from dash.dependencies import Input, Output, State
from urllib.parse import unquote
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import sys,requests

# Import web app
from webapp import app

# Import historian
from historian import Historian

# Parse input parameters
cert=None
average=0
port=80
host='0.0.0.0'
path='.'
size=24*4*31
maxinterval=60
fahrenheit=False
if __name__ == '__main__':
    i=1
    while i<len(sys.argv):
        if sys.argv[i]=='--host':
            i+=1
            host=sys.argv[i]
        elif sys.argv[i]=='--port':
            i+=1
            port=int(sys.argv[i])
        elif sys.argv[i]=='--average':
            i+=1
            average=int(sys.argv[i])
        elif sys.argv[i]=='--path':
            i+=1
            path=sys.argv[i]
        elif sys.argv[i]=='--maxinterval':
            i+=1
            maxinterval=int(sys.argv[i])
        elif sys.argv[i]=='--fahrenheit':
            fahrenheit=True
        elif sys.argv[i]=='--selfsigned':
            cert='adhoc'
        elif sys.argv[i]=='--debug':
            app.debug=True
        elif sys.argv[i]=='--help':
            print('BrewTrend 0.1')
            print('Logs and Displays data from tilt/ispindel')
            print('Fiksdal(C)2021')
            print('')
            print('Usage: '+sys.argv[0]+'')
            print('')
            print('Switches:')
            print('\t--host HOST\tInterface to bind to (Default: 0.0.0.0)')
            print('\t--port PORT\tNetwork port for web gui (Default: 80)')
            print('\t--path PATH\tPath to log data to (Default: cwd)')
            print('\t--average N\tAverage over N samples')
            print('\t--maxinterval S\tFastest allowed interval in seconds')
            print('\t--fahrenheit\tUse fahrenheit instead of celsius')
            print('\t--selfsigned\tUse self-signed certificate for https')
            print('\t--debug\t\tEnable debugging')
            print('')
            exit()
        else:
            print('Invalid parameter: '+sys.argv[i])
            exit()
        i+=1


# Start historian with parsed settings
app.historian=Historian(path,average,size,maxinterval,fahrenheit,app.debug)

# Find existing devices in historian
devices=[]
for key in app.historian.data:
    devices.append(dbc.DropdownMenuItem(key,href='/'+key))
if len(devices):
    device=devices[0]
else:
    device=''
dropdown = dbc.DropdownMenu(
    id='dropdown',
    children=devices,
    nav = True,
    in_navbar = True,
    label = "Module",
)

# Import modules
import ispindel
import tilt

# Add navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="/assets/beer.png", height="40px")),
                        dbc.Col(dbc.NavbarBrand('BrewTrend')),
                    ],
                    align="center",
                ),
                href="/",
            ),
            dbc.NavbarToggler(id="navbar-toggler2"),
            dbc.Collapse(
                dbc.Nav([dropdown],navbar=True),
                id="navbar-collapse2",
                navbar=True,
            ),
            dcc.DatePickerRange(
                id="datepicker",
                with_portal=True,
                clearable=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-4",
)

def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

for i in [2]:
    app.callback(
        Output(f"navbar-collapse{i}", "is_open"),
        [Input(f"navbar-toggler{i}", "n_clicks")],
        [State(f"navbar-collapse{i}", "is_open")],
    )(toggle_navbar_collapse)



# embedding the navigation bar
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='dl_interval',interval=10000,n_intervals=0),
    html.Div(id='cache',style={'display':'none'},children=device),
    navbar,
    html.Div(id='page-content')
])


@app.callback(
        Output('page-content','children'),
        Output('cache','children'),
        Output('dropdown','label'),
        Input('url','pathname'),
        Input('cache','children'))
def display_page(pathname,cache):
    # Sanitize input
    global devices
    if len(pathname)==0 or pathname=='/':
        if len(devices):
            pathname=devices[0].children
    while len(pathname) and pathname[0]=='/':
        pathname=pathname[1:]
    pathname=unquote(pathname)


    if len(app.historian.data)==0:
        return html.Div(html.H1(children='No Devices or Data Found!')),pathname,'No devices found'

    if not pathname in app.historian.data:
        return html.Div(html.H1(children='Device '+pathname+' not found!')),cache,cache

    if app.historian.data[pathname][-1].battery==0:
        return tilt.layout(pathname),pathname,pathname
    else:
        return ispindel.layout(pathname),pathname,pathname

    print('loading:'+str(pathname))


@app.callback(
        Output('dropdown','children'),
        Input('dl_interval','n_intervals'))
def update_devices(n):
    # Look for new devices
    global devices
    hit=True
    for key in app.historian.data:
        hit=False
        for device in devices:
            if device.children==key:
                hit=True
        if hit==False:
            break
    if hit:
        raise PreventUpdate

    # Update device list
    if app.debug: print('Updating devicelist')
    devices=[]
    for key in app.historian.data:
        devices.append(dbc.DropdownMenuItem(key,href='/'+key))
    return devices


# For uwsgi/nginx integration
server=app.server

# Route updates to historian
@server.route("/update/",methods=['GET','POST'])
@server.route("/update",methods=['GET','POST'])
def update_historian():
    if request.method=='POST':
        # Parse POST data to json-string
        data=''
        try:
            if len(request.data):
                # Pass raw data directly
                data=request.data.decode('utf-8')

            elif request.json:
                # Parse JSON object back to JSON string (sigh)
                d=request.json
                for key in d:
                    if len(data):
                        data+=',"'+key+'":"'+str(d[key])+'"'
                    else:
                        data+='{"'+key+'":"'+str(d[key])+'"'
                if len(data): data+='}'

            elif request.form:
                # Parse form to JSON string
                d=request.form.to_dict()
                for key in d:
                    if len(data):
                        data+=',"'+key+'":"'+str(d[key])+'"'
                    else:
                        data+='{"'+key+'":"'+str(d[key])+'"'
                if len(data): data+='}'

            elif len(request.values):
                # Parse argumented form to JSON string
                d=request.values.to_dict()
                for key in d:
                    if len(data):
                        data+=',"'+key+'":"'+str(d[key])+'"'
                    else:
                        data+='{"'+key+'":"'+str(d[key])+'"'
                if len(data): data+='}'

            else:
                print('Error: Unknown POST data is ignored')

        except Exception as e:
            print('Update Error: '+str(e))


        # Process json data
        try:
            if len(data):
                return app.historian.Parse(data)
        except Exception as e:
            print('Registration error: '+str(e))
    else:
        if app.debug: print('GET request received')
    
    return 'Use POST requests to update measurements'

# Start server
if __name__ == '__main__':
    if cert==None:
        app.run_server(host=host,port=port,debug=app.debug,use_reloader=False)
    else:
        app.run_server(host=host,port=port,debug=app.debug,use_reloader=False,ssl_context=cert)
    if app.debug: print('Running')



