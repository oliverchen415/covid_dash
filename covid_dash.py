import requests
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as dh
import pandas as pd
import plotly.express as px

from dash.dependencies import Input, Output
from datetime import date, timedelta, datetime

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

today = date.today()
start_date = today - timedelta(days=7)
status = ["confirmed", "recovered", "deaths"]
country_url = "https://api.covid19api.com/countries"
country_rsp = requests.get(country_url).json()
slug_list = sorted([cnt["Slug"] for cnt in country_rsp])

summary = requests.get("https://api.covid19api.com/summary").json()
global_sum = summary["Global"]
global_stats_df = pd.DataFrame(global_sum, index=[0])
# print(type(global_stats_df["Date"][0]))
global_stats_df.iloc[0, 6] = datetime.strptime(global_stats_df.iloc[0, 6], "%Y-%m-%dT%H:%M:%S.%fZ").date()
global_stats_df.rename(columns={"NewConfirmed": "New Confirmed",
                                "TotalConfirmed": "Total Confirmed",
                                "NewDeaths": "New Deaths",
                                "TotalDeaths": "Total Deaths",
                                "NewRecovered": "New Recovered",
                                "TotalRecovered": "Total Recovered"
                                },
                       inplace=True)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "COVID-19 Analysis"

app.layout = dh.Div(
    children=[
        dh.Div(
            dcc.ConfirmDialog(
                id="confirm",
                message="Data unavailable, try another place."
                ),
            ),
        dh.Div(
            children=[
                dh.H1(
                    children="COVID-19 Analysis ",
                    className="header-title",
                    ),
                dh.P(
                    children="Examine the most recent week of COVID-19 cases.",
                    className="header-description",
                    ),
                dh.P(
                    children="API used: https://covid19api.com/",
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
                                id="status",
                                options=[{"label": i.title(), "value": i} for i in status],
                                value="confirmed",
                                labelStyle={"display": "inline-block"}
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
                            options=[{"label": i.title(), "value": i.title()} for i in slug_list],
                            value="Belgium",
                        )
                    ],
                    style={"width": "25%"},
                ),
            ],
            className="menu",
        ),
        dh.Div(
            children=[
                dh.Div(
                    dcc.Graph(
                        id="graph",
                        config={"displayModeBar": False}
                        ),
                    className="card"
                    )
                ],
            className="wrapper"
            ),
        dh.Div(
            children=[
                dh.Div(
                        children="Global Statistics",
                        className="menu-title"
                        ),
                dh.Div(
                    dash_table.DataTable(
                        id="table",
                        columns=[{"name": i, "id": i} for i in global_stats_df.columns],
                        data = global_stats_df.to_dict("records"),
                        style_header={ "border": "1px solid black" },
                        style_cell={
                                    "border": "1px solid grey",
                                    "textAlign": "left"
                                    },
                        ),
                    className="card"
                    )
                ],
            className="wrapper"
            ),
        ]
    )


@app.callback(
    [Output("graph", "figure")],
    [Input("country", "value"),
    Input("status", "value")]
)
def update_graph(country, status):
    endpoint = f"https://api.covid19api.com/country/{country}/status/{status}"
    params = {"from": str(start_date), "to": str(today)}

    response = requests.get(endpoint, params=params).json()
    norm_data = pd.json_normalize(response)
    if norm_data.empty:
        return dash.no_update
    else:
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

@app.callback(
    Output("confirm", "displayed"),
    Input("country", "value"),
    Input("status", "value")
)
def error_notice(country, status):
    endpoint = f"https://api.covid19api.com/country/{country}/status/{status}"
    params = {"from": str(start_date), "to": str(today)}

    response = requests.get(endpoint, params=params).json()
    norm_data = pd.json_normalize(response)
    if norm_data.empty:
        return True


if __name__ == "__main__":
    app.run_server(debug=True)