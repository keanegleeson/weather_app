from dash import Dash, dcc, html, Input, Output, callback

import pandas as pd
import requests

app = Dash(__name__)

app.layout = html.Div(
    [
        html.Button("Update Position", id="update_btn"),
        dcc.Geolocation(id="geolocation"),
        html.Div(id="text_position"),
    ]
)


@callback(Output("geolocation", "update_now"), Input("update_btn", "n_clicks"))
def update_now(click):
    return True if click and click > 0 else False


@callback(
    Output("text_position", "children"),
    Input("geolocation", "local_date"),
    Input("geolocation", "position"),
)
def display_output(date, pos):
    if pos:
        latitude = str(pos['lat'])
        longitude = str(pos['lon'])
        
        return latitude, longitude,  html.P(
            f"As of {date} your location was: lat {pos['lat']},lon {pos['lon']}, accuracy {pos['accuracy']} meters",
        )
    return "No position data available"

if __name__ == "__main__":
    app.run(debug=True)

exit()


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd
import requests


#initialize app
app = dash.Dash(__name__)
app.title = "Weather App"
server = app.server  # Required for deployment on platforms like Heroku

#determine layout
app.layout = html.Div(
    [
        html.H1("Weather App"),
        html.Button("Get Weather", id="update_btn"),
        dcc.Geolocation(id="geolocation"),
        html.Div(id="weather-output"),
    ]
)

def get_hourly_forecast(lat, lon):
    base_url = "https://api.weather.gov/points/"+lat+","+lon
    headers = {"token": "yfeEyUrYONqEWtsmkDphdBxNkuHIIEXw"}
    # params = {}

    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data["results"]
    else:
        return None


#get data at a certain location
def get_weather_data(location):
    base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": "yfeEyUrYONqEWtsmkDphdBxNkuHIIEXw"}
    params = {
        "datasetid": "GHCND",  # Global Historical Climatology Network - Daily
        "datatypeid": "TMAX",   # Maximum Temperature
        "limit": 5,            # Number of results to fetch
        "location": location,
        "units": "metric",     # You can change to "standard" or "imperial" as per your preference
    }

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data["results"]
    else:
        return None

# callback to display weather data on the dashboard:
@callback(Output("geolocation", "update_now"), Input("update_btn", "n_clicks"))
def update_now(click):
    return True if click and click > 0 else False

@callback(
    Output("weather-output", "children"),
    Input("geolocation", "local_date"),
    Input("geolocation", "position"),
)
def display_weather_data(date, pos):
    if pos:
        latitude, longitude = pos["latitude"], pos["longitude"]
        location = f"{latitude},{longitude}"
        weather_data = get_weather_data(location)

        if weather_data:
            df = pd.DataFrame(weather_data)
            return html.Div([
                html.H3(f"Weather data for your current location:"),
                dcc.Graph(
                    id='weather-graph',
                    figure={
                        'data': [
                            {'x': df['date'], 'y': df['value'], 'type': 'line', 'name': 'Max Temperature'},
                        ],
                        'layout': {
                            'title': 'Maximum Temperature',
                            'xaxis': {'title': 'Date'},
                            'yaxis': {'title': 'Temperature (°C)'},
                        }
                    }
                ),
                html.P("Data source: NOAA API"),
            ])
        else:
            return html.Div("API request failed.")
    return "No position data available"


if __name__ == "__main__":
    app.run_server(debug=True)
