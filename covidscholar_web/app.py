import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

from covidscholar_web.view import footer_html, query_helpers_html, results_html, display_all_html, most_recent_html
import covidscholar_web.search as search
from covidscholar_web.constants import *

external_scripts = [
    "https://www.googletagmanager.com/gtag/js?id=UA-149443072-3"
]

app = dash.Dash(__name__, external_scripts=external_scripts)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.config.suppress_callback_exceptions = True
app.title = "COVID-19 Scholar"

footer_interior = footer_html()
footer_section = html.Div(footer_interior, className="section")
footer = html.Footer(footer_section, className="footer has-margin-top-50")


external_stylesheets = html.Link(
    href="https://fonts.googleapis.com/css?family=Lato&display=swap",
    rel="stylesheet",
    className="is-hidden",
)

logo = html.Div(
    html.A(
        html.Img(
            src="/assets/covidscholar_logo.png",
            style={"width": "400px", "height": "150px"}
        ),
        href="http://www.covidscholar.com",
        target="_blank"
    )
)

powered_by = html.Div(
    html.A(
        html.Img(
            src="/assets/powered-by.png", style={"width": "400px", "height": "56px"}
        ),
        href="https://www.matscholar.com",
        target="_blank"
    )
)

all_logos = html.Div([logo, powered_by])

header_centering = html.Div(
    all_logos,
    className="columns is-centered is-mobile",
)

header_container = html.Div(
    header_centering,
    className="has-margin-bottom-30 has-margin-top-50",
)

# The container for individual apps

app_container = html.Div(
    html.Div(
        html.Div(
            [
                query_helpers_html(),
                html.Div(
                    dcc.Loading(
                        html.Div(id="results-area"),
                        type="circle"
                    ),
                    className="has-margin-top-50"
                )
            ],
            className="column is-two-thirds"
        ),
        className="columns is-centered"
    ),
    className="msweb-fade-in"

)

app_expander = html.Div(
    app_container, className="msweb-is-tall has-margin-20"
)
app_expander_container = html.Div(
    app_expander,
    className="msweb-is-tall-container msweb-fade-in has-margin-top-50",
)

core_view = html.Div(
    [external_stylesheets, header_container, app_expander_container, footer],
    className="msweb-background msweb-fade-in",
)

app.layout = core_view


@app.callback(
    Output("results-area", "children"),
    [Input("main-input", "n_submit")],
    [State("main-input", "value")]
)
def show_search_results(input_n_submit, text):
    # all_n_searches = [0 if n is None else n for n in [go_button_n_clicks, input_n_submit]]
    if input_n_submit is None:
        #On page load show the most recent papers
        most_recent = search.most_recent()
        results = most_recent_html(most_recent)
        return results
    else:
        print("doing search")
        if text is None:
            results = display_all_html(search.get_all())
        else:
            abstracts = search.search_abstracts(text, limit=max_results)
            # print(abstracts)
            print(len(abstracts["full"]), len(abstracts["partial"]))
            results = results_html(abstracts)
        return results
    # else:
    #     print("doing get all")
    #     results = display_all_html(search.get_all())
    #     return results

    
# @app.callback([Output("modal{}".format(i), "style") for i in range(max_results)],
#               [Input("similar_display_button{}".format(i), 'n_clicks')
#                for i in range(max_results)]
#               )
# def show_similar_abstracts(*similar_display_button_n_clicks):
#     styles = []
#     for button_n_clicks in similar_display_button_n_clicks:
#         if button_n_clicks is not None and button_n_clicks % 2 == 1:
#             styles.append({"display": "block"})
#         else:
#             styles.append({"display": "none"})
#     return styles
