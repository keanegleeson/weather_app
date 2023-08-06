from dash import Dash, dcc, html, Input, Output
import requests
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Hourly Weather Forecast"),
    html.Button('Update Weather', id='weather-update', n_clicks=0),
    dcc.Graph(id='weather-plot'),
    html.Div(id='weather-table-container', style={'overflowX': 'auto'}),
])

# Create a dictionary to map weather status to icon URLs
icon_mapping = {
    'Isolated Showers And Thunderstorms': 'https://cdn-icons-png.flaticon.com/128/1163/1163661.png',
    'Mostly Sunny': 'https://cdn-icons-png.flaticon.com/128/1163/1163661.png',
    'Partly Sunny': 'https://cdn-icons-png.flaticon.com/128/1146/1146869.png',
    'Sunny': 'https://cdn-icons-png.flaticon.com/128/4814/4814268.png',
    'Mostly Clear': 'https://cdn-icons-png.flaticon.com/128/414/414927.png',
    'Slight Chance Rain Showers': 'https://cdn-icons-png.flaticon.com/128/4735/4735072.png',
    'Chance Showers And Thunderstorms': 'https://cdn-icons-png.flaticon.com/128/1146/1146860.png',
    'Showers And Thunderstorms Likely': 'https://cdn-icons-png.flaticon.com/128/1146/1146860.png',
    'Mostly Cloudy': 'https://cdn-icons-png.flaticon.com/128/1163/1163624.png',
}

def get_weather_data():
    url = "https://api.weather.gov/gridpoints/LMK/50,76/forecast/hourly"
    headers = {"Accept": "application/geo+json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data["properties"]["periods"]
    else:
        return None

def get_icon_url(short_forecast):
    return icon_mapping.get(short_forecast, 'https://cdn-icons-png.flaticon.com/128/1163/1163661.png')

@app.callback(
    Output('weather-plot', 'figure'),
    Output('weather-table-container', 'children'),
    Input('weather-update', 'n_clicks')
)
def update_weather_data(n_clicks):
    if n_clicks is None:
        return dash.no_update

    weather_data = get_weather_data()

    if weather_data:
        df = pd.DataFrame(weather_data)

        # Add a new column for the icon URLs based on the weather status
        df['icon_url'] = df['shortForecast'].apply(get_icon_url)
        
        fig = {
            'data': [
                {'x': df['startTime'], 'y': df['temperature'], 'type': 'scatter', 'name': 'Temperature (F)'},
            ],
            'layout': {
                'title': 'Hourly Temperature Forecast',
                'xaxis': {'title': 'Time'},
                'yaxis': {'title': 'Temperature (°F)'},
            }
        }

        table_rows = []
        for index, data in df.iterrows():
            table_row = html.Tr(
                [
                    html.Td(data["startTime"], style={'border': '1px solid #ddd'}),
                    html.Td(data["temperature"], style={'border': '1px solid #ddd'}),
                    html.Td(data["relativeHumidity"]["value"], style={'border': '1px solid #ddd'}),
                    html.Td(data["windSpeed"], style={'border': '1px solid #ddd'}),
                    html.Td(data["windDirection"], style={'border': '1px solid #ddd'}),
                    html.Td(data["shortForecast"], style={'border': '1px solid #ddd'}),
                    html.Td(html.Img(src=data["icon_url"], width=40, height=40), style={'border': '1px solid #ddd'}),
                ],
                style={'background-color': '#f2f2f2'},
                className='hoverable-row'
            )
            table_rows.append(table_row)

        table = html.Table(
            id='weather-table',
            children=[
                html.Thead(
                    html.Tr([
                        html.Th("Time"),
                        html.Th("Temperature (F)"),
                        html.Th("Humidity (%)"),
                        html.Th("Wind Speed (mph)"),
                        html.Th("Wind Direction"),
                        html.Th("Forecast"),
                        html.Th(""),
                    ])
                ),
                html.Tbody(table_rows),
            ],
            style={'border-collapse': 'collapse', 'width': '100%'}
        )

        return fig, table
    else:
        return dash.no_update, html.Div("API request failed.")


if __name__ == '__main__':
    app.run_server(debug=True)
