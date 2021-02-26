import requests
import dash
import dash_core_components as dcc
import dash_html_components as dh
import pandas as pd
import plotly.express as px

from dash.dependencies import Input, Output
from datetime import date, datetime

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

today = date.today()
vac_datetime = datetime.strptime("Dec 10, 2020", "%b %d, %Y")
vac_date = datetime.date(vac_datetime)
# start_date = today - timedelta(days=75)
delta = today - vac_date
start_date = today - delta
status = ["confirmed", "recovered", "deaths"]
country_url = "https://api.covid19api.com/countries"
country_rsp = requests.get(country_url).json()
country_list = []
for cnt in country_rsp:
    country_list.append(cnt["Country"])
country_list = sorted(country_list)



app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "COVID-19 Analysis"

app.layout = dh.Div(
    children=[
        dh.Div(
            children=[
                dh.H1(children="COVID-19 Analysis ", className="header-title"),
                dh.P(children="Analyze the effect of the COVID vaccine on the number of cases from "
                     "date of the first known vaccination",
                    className="header-description",
                        ),
            ],
            className="header",
        ),
        dh.Div(
            children=[
                dh.Div(
                    children=[
                        dh.Div(
                            children="Data to Lookup",
                            className="menu-title"
                        ),
                        dh.Div(
                            dcc.RadioItems(
                                id='status',
                                options=[{'label': i.title(), 'value': i} for i in status],
                                value="confirmed",
                                labelStyle={'display': 'inline-block'}
                            ),
                        ),
                    ]
                ),
                dh.Div(
                    children=[
                        dh.Div(
                            children="Country",
                            className="menu-title"
                        ),
                        dcc.Dropdown(
                            id="country",
                            options=[{'label': i, 'value': i} for i in country_list],
                            value="Belgium",
                        )
                    ],
                ),
            ],
            className="menu",
        ),
        dh.Div(
            children=[
                dcc.Graph(
                    id='graph',
                    config={"displayModeBar": False}
                    )
                ],
            className="wrapper"
            )
        ]
    )


@app.callback(
    Output("graph", "figure"),
    Input("country", "value"),
    Input("status", "value")
)
def update_graph(country, status):
    endpoint = f"https://api.covid19api.com/country/{country}/status/{status}"
    params = {"from": str(start_date), "to": str(today)}

    response = requests.get(endpoint, params=params).json()
    norm_data = pd.json_normalize(response)
    norm_data = norm_data[norm_data["Province"] == ""]

    fig = px.line(
        norm_data,
        x="Date",
        y="Cases",
        title=f"COVID-19 Data for {country}",
        labels={
            "Date": "Date",
            "Cases": "Cases"
        }
        )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)