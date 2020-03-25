import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
from covidscholar_web.constants import *
import random
from datetime import datetime as dt
from urllib.parse import urlencode

def query_helpers_html():
    input_box = html.Div(
        dcc.Input(
            id="main-input",
            className="input is-large is-rounded",
            placeholder="Enter search terms or keywords",
            autoFocus=True,
            style={
                'inputmode': 'search'}
        ),
        className="column is-full"
    )

    input_row = html.Div(
        html.Div(
            [input_box],
            className="columns is-centered"
        ),
        className="has-margin-left-50 has-margin-right-50"
    )

    inner_label_styles = "is-size-4 has-text-weight-bold"
    outer_div_styles = "has-text-centered has-margin-10"

    # date_picker = dcc.DatePickerRange(
    #     id='my-date-picker-range',
    #     min_date_allowed=dt(1995, 8, 5),
    #     max_date_allowed=dt(2017, 9, 19),
    #     initial_visible_month=dt(2017, 8, 5),
    #     end_date=dt(2017, 8, 25),
    #     className="",
    # )

    selectors = html.Div(
        [html.A("Help this effort by submitting document summaries and keywords",
                href="https://docs.google.com/forms/d/e/1FAIpQLSf4z7LCBizCs6pUgO3UyfxJMCAVC-bRh3cvW7uNghDu4UeBig/viewform?usp=sf_link", target="_blank")],
        className="columns is-centered is-vcentered has-margin-top-10"
    )

    return html.Div(
        [
            html.Div(html.Label("Search research related to COVID-19",
                                className="is-size-3 has-text-weight-semibold"),
                     className=outer_div_styles),
            input_row,
            selectors
        ],
    )


def results_area_html():
    return ""


def footer_html():
    """
    Make the footer for all apps.

    Returns:
        (dash_html_components.Div): The footer as an html block.

    """
    note_div = html.Div(
        [
            dcc.Markdown(
                "This website uses natural language processing (NLP) to power search on a set of research papers related to COVID-19."
                " It was created by the team behind [Matscholar](https://www.matscholar.com), a research effort led by the [HackingMaterials](https://hackingmaterials.lbl.gov), "
                " [Persson](https://perssongroup.lbl.gov), and [Ceder](https://ceder.berkeley.edu) research"
                " groups at Lawrence Berkeley National Lab."
                " The virus icon in our logo was made by Freepik from www.flaticon.com",
                className="column is-half is-size-6"
            )
        ],
        className="columns is-centered"

    )

    common_footer_style = "has-text-weight-bold"

    about_matscholar = html.A(
        "About Matscholar",
        href="https://github.com/materialsintelligence/matscholar-web",
        target="_blank",
        className=common_footer_style,
    )

    privacy_policy = html.A(
        "Privacy Policy",
        href="https://www.iubenda.com/privacy-policy/55585319",
        target="_blank",
        className=common_footer_style,
    )

    submit_feedback = html.A(
        "Matscholar Forum",
        href="https://discuss.matsci.org/c/matscholar",
        target="_blank",
        className=common_footer_style,
    )

    footer_link_tree = html.Div(
        [
            about_matscholar,
            html.Span(" | "),
            privacy_policy,
            html.Span(" | "),
            submit_feedback,
        ]
    )

    footer_copyright = html.Div(
        html.Span("Copyright © 2019 - Materials Intelligence")
    )

    footer = html.Div(
        [note_div, footer_link_tree, footer_copyright],
        id="footer_container",
        className="content has-text-centered",
    )

    footer_container = html.Div(footer)
    return footer_container


def results_html(results_dict, max_results_shown=30, full_match_threshold=10, show_all=False):
    """
    Get the html block for abstracts results from the list of results

    Args:
        results_dict (list of dict): List of results_dict

    Returns:
        (dash_html_components.Div): The results_dict results html block.

    """

    partial_matches = [r for r in results_dict["partial"] if "error" not in r]
    full_matches = [r for r in results_dict["full"] if "error" not in r]
    all_matches = partial_matches + full_matches

    if len(all_matches) == 0:
        return no_results_html()
    else:
        common_label_classname = "has-margin-top-10 has-margin-bottom-10 is-size-3 has-text-weight-semibold"
        full_matches = full_matches[:max_results_shown]
        n_remaining = max_results_shown - len(full_matches)
        partial_matches = partial_matches[:n_remaining]

        if not show_all:

            if len(full_matches) >= full_match_threshold:

                if len(full_matches) > full_match_threshold:
                    formatted_n_full_matches = f"{max_results_shown}+"
                else:
                    formatted_n_full_matches = f"{len(full_matches)}"

                if len(full_matches) == 1:
                    overhead_label = html.Div(
                        f"Found {formatted_n_full_matches} exact match",
                        className=common_label_classname
                    )
                else:
                    overhead_label = html.Div(
                        f"Found {formatted_n_full_matches} exact matches",
                        className=common_label_classname
                    )

                formatted_results = [format_result_html(
                    match) for match in full_matches]
                paper_table = html.Table(
                    formatted_results,
                    className="table is-fullwidth is-bordered is-hoverable is-narrow is-striped",
                )
                results_elements = [paper_table]

            elif len(full_matches) < full_match_threshold:

                if partial_matches:
                    partial_label = html.Div(
                        f"({len(partial_matches)} additional partial matches included)",
                        className="is-size-3 has-text-weight-semibold has-margin-bottom-10 has-margin-top-50"
                    )
                    partial_matches_results = [format_result_html(
                        match) for match in partial_matches]
                    paper_table_partial = html.Table(
                        partial_matches_results,
                        className="table is-fullwidth is-bordered is-hoverable is-narrow is-striped",
                    )
                else:
                    partial_label = html.Div(
                        f"No additional partial matches found",
                        className="is-size-3 has-text-weight-semibold has-margin-bottom-10 has-margin-top-50"
                    )
                    paper_table_partial = html.Div(children="")

                if len(full_matches) == 0:
                    overhead_label = html.Div(
                        [
                            html.Div(
                                f"Found no exact matches",
                                className=common_label_classname
                            ),
                            html.Div(
                                f"No exact matches found. Using partial matches only.",
                                className="is-size-5 has-text-weight-bold"
                            )
                        ]
                    )
                    results_elements = [partial_label, paper_table_partial]
                else:
                    if len(full_matches) == 1:
                        overhead_label = html.Div(
                            f"Found {len(full_matches)} exact match",
                            className=common_label_classname
                        )
                    else:
                        overhead_label = html.Div(
                            f"Found {len(full_matches)} exact matches",
                            className=common_label_classname
                        )
                    full_label = html.Div(
                        f"Exact matches",
                        className=common_label_classname
                    )
                    full_matches_results = [format_result_html(
                        match) for match in full_matches]
                    paper_table_full = html.Table(
                        full_matches_results,
                        className="table is-fullwidth is-bordered is-hoverable is-narrow is-striped",
                    )

                    results_elements = [
                        full_label, paper_table_full, partial_label, paper_table_partial]
            else:
                formatted_results = [format_result_html(
                    match) for match in full_matches]
                formatted_results += [format_result_html(
                    match) for match in partial_matches]

            # entities_keys = []
            # for e in valid_entity_filters:
            #     color = entity_color_map[e]
            #     entity_colored = html.Div(
            #         e,
            #         className=f"msweb-is-{color}-txt is-size-5 has-text-weight-bold",
            #     )
            #     entity_key = html.Div(
            #         entity_colored, className=f"box has-padding-5"
            #     )
            #     entity_key_container = html.Div(
            #         entity_key, className="flex-column is-narrow has-margin-5"
            #     )
            #     entities_keys.append(entity_key_container)
            # entity_key_container = html.Div(
            #     entities_keys, className="columns is-multiline has-margin-5"
            # )

        return html.Div(
            [
                overhead_label,
                html.Div(
                    results_elements
                ),
            ],
            className="has-margin-top-20 has-margin-bottom-20 msweb-fade-in"
        )


def most_recent_html(results):
    """
    Get the html block for the most recent results

    Args:
        results (list of dict): List of results_dict

    Returns:
        (dash_html_components.Div): The results_dict results html block.

    """

    if len(results) == 0:
        return no_results_html()
    else:
        common_label_classname = "has-margin-top-10 has-margin-bottom-10 is-size-3 has-text-weight-semibold"

        overhead_label = html.Div(
            f"Recently submitted to the repository (updates every ~15 min)",
            className=common_label_classname
        )

        formatted_results = [format_result_html(
            result) for result in results]
        paper_table = html.Table(
            formatted_results,
            className="table is-fullwidth is-bordered is-hoverable is-narrow is-striped",
        )
        results_elements = [paper_table]

        return html.Div(
            [
                overhead_label,
                html.Div(
                    results_elements
                ),
            ],
            className="has-margin-top-20 has-margin-bottom-20 msweb-fade-in"
        )


def display_all_html(results):
    common_label_classname = "has-margin-top-10 has-margin-bottom-10 is-size-3 has-text-weight-semibold"

    overhead_label = html.Div(
        "Showing all submitted documents:",
        className=common_label_classname
    )

    full_matches_results = [format_result_html(
        match) for match in results]

    results_elements = html.Table(
        full_matches_results,
        className="table is-fullwidth is-bordered is-hoverable is-narrow is-striped",
    )

    return html.Div(
        [
            overhead_label,
            html.Div(
                results_elements
            ),
        ],
        className="has-margin-top-20 has-margin-bottom-20 msweb-fade-in"
    )


"""
Internal Functions
"""


def common_null_warning_html(text, alignment="center", top_margin=50):
    """
    Get a null warning html block which can be used across all apps. Useful for
    when no text is entered into a box, etc.

    Args:
        text (str): The null warning text.
        alignment (str): Either "center" or "left".
        top_margin (int): The top margin, in pixels.

    Returns:
        (dash_html_components.Div): The common null warning html block.

    """
    if alignment in ["center", "left"]:
        align = "has-text-centered" if alignment == "center" else ""
    else:
        raise ValueError(
            f"Invalid alignment: {alignment}. Must be 'center' or 'left'."
        )

    null_txt = html.Div(text, className="is-size-4")
    null_container = html.Div(
        null_txt, className=f"container {align} has-margin-top-{top_margin}"
    )
    return null_container


def no_results_html():
    """
    The html block for displaying no results.


    Returns:
        (dash_html_components.Div): The html block for no results.

    """
    return common_null_warning_html(
        "No results found!", alignment="center"
    )


def divider_html():
    """
    Get an html block divider. Can be used in any app.

    Returns:
        (dash_html_components.Div): The divider html block.

    """
    return html.Div(html.Hr(className="is-divider"))


def format_result_html(result):
    """
    Converts a single row of the abstracts results dataframe and gives back
    the plotly dash html row to be formatted in a table of abstracts.
    Title of the paper is the first line
    Author 1, Author 2... - Title of Journal, Year - Publisher
    First 200 characters of abstract.
    Entities
    Args:
        result (pd.Series: Row of dataframe to be formatted for display.
    Returns:
        (dash_html_components.Tr): The table row html block for the formatted
            result.
    """

    title = result.get("title", None)

    if title is None or len(title) == 0:
        title = result.get("doi", None)
        if title is None or len(title) == 0:
            title = result['link']

    title_link = html.A(title, href=result["link"], target="_blank")

    title = html.Div(
        title_link, className="is-size-4 has-text-link has-text-weight-bold"
    )

    # Format the 2nd line "authors - journal, year" with ellipses for overflow
    characters_remaining = 90  # max line length
    characters_remaining -= 5  # spaces, '-', and ','

    date = result.get('publication_date', None)
    if date is None:
        date = ""
    if len(date) > 10:
        date = date[0:10]

    # if date is not None:
    #     date_iso = date["date-time"]
    #     date = date_iso[5:7] + "/" + date_iso[8:10] + "/" + date_iso[0:4]
    # else:
    #     date = ""
    characters_remaining -= len(date)

    journal = result.get("journal", "")
    if journal is None or len(journal) == 0:
        journal = ""
    if isinstance(journal, list):
        journal = journal[0]

    short_journal = ""
    # journal = metadata.get("container-title", "")
    # short_journal = metadata.get("short-container-title", "")
    # if isinstance(journal, list) and len(journal) > 0:
    #     journal = journal[0]
    # else:
    #     journal = ""

    # if isinstance(short_journal, list) and len(short_journal) > 0:
    #     short_journal = short_journal[0]
    # else:
    #     short_journal = ""

    # if len(journal) == 0 and len(short_journal) > 0:
    #     journal = short_journal

    if len(journal) > 20:
        if len(short_journal) > 0:
            journal = short_journal
        else:
            journal = journal[0:30] + "..."
    characters_remaining -= len(journal)

    authors_obj = result.get('authors', [])
    full_author_list = []
    for author in authors_obj:
        if "name" in author:
            full_author_list.append(author["name"])
        elif "Name" in author:
            full_author_list.append(author["Name"])
    num_authors = len(full_author_list)
    reduced_author_list = []
    while len(full_author_list) > 0:
        author = full_author_list.pop(0)
        if characters_remaining > len(author):
            reduced_author_list.append(author)
            characters_remaining -= len(author) + 2
    authors = ", ".join(reduced_author_list)
    if len(reduced_author_list) < num_authors:
        authors += "..."

    conditional_dash = " - " if len(journal) > 0 else ""
    conditional_comma = ", " if len(date) > 0 else ""

    ajy = f"{authors}{conditional_dash}{journal}{conditional_comma}{date}"
    authors_journal_and_year = html.Div(
        ajy, className="is-size-5 msweb-is-green-txt "
    )

    abstract_txt = result["abstract"]
    abstract = html.Div(abstract_txt, className="is-size-6 has-margin-5")

    summary = result.get("summary_human", "")
    if summary is not None and len(summary) > 0:
        if isinstance(summary, str):
            summary = [summary]

        # summary = "\n__________________\n".join(summary)

        summary_label = html.Div(
            "User-submitted {}:".format("summary" if (len(summary) == 1) else "summaries"),
            className="has-margin-5 has-text-weight-bold"
        )

        summary = html.Div([html.Div(s, className="columns is-multiline has-margin-5 msweb-is-purple-txt") for s in summary])

        keywords_label = html.Div(
            "User-submitted keywords:", className="has-margin-5 has-text-weight-bold"
        )

        keywords = html.Div(
            ", ".join(result["keywords"]),
            className="columns is-multiline has-margin-5 has-text-weight-bold msweb-is-dimgray-txt"
        )

        paper_div = html.Div(
            [title, authors_journal_and_year, abstract, summary_label, summary, keywords_label, keywords],
            className="has-margin-10",
        )
    else:

        summary_label = html.Div(
            "No user-submitted summary available:", className="has-margin-5 has-text-weight-bold"
        )

        # generate pre-filled link to Google Form
        gf_link_parameters = {"link": "entry.101149199",
                              "doi": "entry.1258141481",
                              "abstract": "entry.112702407",
                              }

        gf_link_prefilled = "https://docs.google.com/forms/d/e/1FAIpQLSf4z7LCBizCs6pUgO3UyfxJMCAVC-bRh3cvW7uNghDu4UeBig/viewform?usp=pp_url&"
        params = {}
        for key in gf_link_parameters:
            if key in result and not (result[key] is None) and len(result[key]) > 0:
                params[gf_link_parameters[key]] = result[key]
        summary = html.A("Submit a summary for this article.",
                         href=gf_link_prefilled+urlencode(params),
                         target="_blank",
                         className="a has-margin-10 msweb-is-red-link ")

        paper_div = html.Div(
            [title, authors_journal_and_year, abstract, summary_label, summary],
            className="has-margin-10",
        )

    table_cell = html.Td(paper_div)
    return html.Tr(table_cell)


def format_authors(author_list):
    """
    Format the authors to a readable list for later formatting.

    Args:
        author_list (str, [str]): The "dirty" list of strings or string
            containing all author names.

    Returns:
        [str]: The "clean" list of author names.
    """
    if isinstance(author_list, (list, tuple)):
        return ", ".join([format_authors(author) for author in author_list])
    else:
        if ", " in author_list:
            author_list = author_list.split(", ")
            author_list.reverse()
            author_list = " ".join(author_list)
        elif "," in author_list:
            author_list = author_list.split(",")
            author_list.reverse()
            author_list = " ".join(author_list)
        return author_list


def modal(id, content):
    return html.Div(
        children=[
            html.Div([
                content
            ])],
        id=id,
        className='has-margin-bottom-20',
        style={"display": "none"},
    )


def format_similar_abstracts(abstract):
    """
    Formats the div to display similar abstracts
    Args:
        abstract (pd.Series: Row of dataframe to be formatted for display.

    Returns:
        (dash_html_components.Div): The html for the similar abstracts
    """

    similar_abstracts_html = [format_similar_abstract(
        a) for a in abstract['similar_abstracts']]
    similar_div = html.Div(
        similar_abstracts_html,
        className="has-margin-10"
    )

    return similar_div


def format_similar_abstract(similar_abstract):
    """
    Formats the div to display a single similar abstract
    Args:
        similar_abstract (pd.Series: Row of dataframe to be formatted for display.

    Returns:
        (dash_html_components.Div): The html for the similar abstract
    """

    title_link = html.A(
        similar_abstract["title"], href=similar_abstract["link"], target="_blank")

    title = html.Div(
        title_link, className="is-size-5 has-text-link has-text-weight-bold"
    )

    # Format the 2nd line "Session - Time, Date, Room"
    characters_remaining = 90  # max line length
    characters_remaining -= 5  # spaces, '-', and ','

    session = similar_abstract["session"]
    characters_remaining -= len(session)

    datetime = similar_abstract["datetime"].strftime("%A %b %d %I:%M %p")
    characters_remaining -= len(datetime)

    room = similar_abstract['room']
    characters_remaining -= len(room)

    session = html.Span(session, className="is-size-6 has-text-weight-bold")
    sep = html.Span(" - ", className="is-size-6")
    date = html.Span(datetime, className="is-size-6 msweb-is-blue-txt")
    at = html.Span(" @ ", className="is-size-6")
    room = html.Span(room, className="is-size-6 msweb-is-green-txt")
    session_date_room = html.Div(
        [session, sep, date, at, room],
        # className="msweb-is-blue-txt"
    )

    # Format the 3rd line "Authors" with ellipses for overflow
    characters_remaining = 90  # max line length

    authors = similar_abstract['authors'].replace(",,", ",")
    full_author_list = authors.split(",")
    num_authors = len(full_author_list)
    reduced_author_list = []
    while len(full_author_list) > 0:
        author = full_author_list.pop(0)
        if characters_remaining > len(author):
            reduced_author_list.append(author)
            characters_remaining -= len(author) + 2
    authors = ", ".join(reduced_author_list)
    if len(reduced_author_list) < num_authors:
        authors += "..."
    authors = authors.replace(",,", ",")

    # get rid of pesky trailing commas
    authors = authors.strip()
    if authors[-1] == ",":
        authors = authors[:-1]

    authors = html.Div(
        authors, className="is-size-6 has-text-weight-semibold"
    )

    characters_remaining = 90
    affiliations = similar_abstract['affiliations'].replace(",", ", ")
    if len(affiliations) > characters_remaining:
        affiliations = affiliations[:characters_remaining - 3] + "..."

    affiliations = html.Div(
        affiliations, className="is-size-6 msweb-is-grey-txt"
    )

    # max_abstract_chars = 1000
    abstract_txt = similar_abstract["abstract"]
    # if len(abstract_txt) > max_abstract_chars:
    #     abstract_txt = abstract_txt[:max_abstract_chars] + "..."
    # abstract = html.Div(abstract_txt, className="is-size-6 has-margin-bottom-20")
    abstract = format_expandable_abstract(abstract_txt)

    similar_div = html.Div(
        html.Div(
            [title, session_date_room, authors, affiliations, abstract],
            className="box has-margin-10 msweb-fade-in"
        ),
    )

    return similar_div


def format_expandable_abstract(abstract_txt):
    """
    Format the similar abstracts in an expandable format where you can see the title etc. but the full abstract
    text is hidden.

    Args:
        abstract_txt (str): The full abstract text.

    Returns:
        The html block

    """
    toggle_button = html.Div("Toggle full abstract",
                             className="button is-link is-size-7 is-inverted")
    summary = html.Summary(toggle_button)
    details = html.Details(
        [
            summary,
            html.Div(abstract_txt, className="is-size-6 msweb-fade-in")
        ]
    )
    return details
