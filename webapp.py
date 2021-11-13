#
# Loads DASH with title and appropriate style sheet
#
import dash_bootstrap_components as dbc
import dash,requests

# Load dash application
app=dash.Dash(__name__,title='BrewTrend',external_stylesheets=[dbc.themes.DARKLY])
app.config.suppress_callback_exceptions=True
app.historian=None
app.debug=False

