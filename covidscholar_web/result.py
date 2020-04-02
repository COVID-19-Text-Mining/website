import dash_core_components as dcc
import dash_html_components as html
from urllib.parse import urlencode


def get_formatted_authors(result, characters_remaining):
    """

    Args:
        result: (dict) entry to get authors from
        characters_remaining: (int) number of characters remaining in line

    Returns:
        (str), (int): Formatted author list and number of remaining characters in line

    """
    authors_obj = result.get('authors', [])
    if authors_obj is None:
        authors_obj = []
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

    return authors, characters_remaining


def get_formatted_journal(result, characters_remaining):
    """

    Args:
        result: (dict) db entry
        characters_remaining: (int) number of characters remaining in field

    Returns:
        (str) name of journal, (int) number of characters remaining in line
    """
    journal_obj = result.get("journal", "")
    if journal_obj is None or len(journal_obj) == 0:
        journal = ""
    elif isinstance(journal_obj, list):
        journal = journal_obj[0]
    else:
        # should be a string by this point
        journal = journal_obj

    short_journal = ""

    if len(journal) > 20:
        if len(short_journal) > 0:
            journal = short_journal
        else:
            journal = journal[0:30] + "..."
    characters_remaining -= len(journal)
    return journal, characters_remaining


def get_formatted_date(result, characters_remaining):
    date = result.get('publication_date', None)
    if date is None:
        date = ""
    if len(date) > 10:
        date = date[0:10]

    characters_remaining -= len(date)
    return date, characters_remaining


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

    journal, characters_remaining = get_formatted_journal(result, characters_remaining)

    authors, characters_remaining = get_formatted_authors(result, characters_remaining)

    date, characters_remaining = get_formatted_date(result, characters_remaining)

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

        summary = html.Div(
            [html.Div(s, className="columns is-multiline has-margin-5 msweb-is-purple-txt") for s in summary])

        keywords_human_label = html.Div(
            "User-submitted keywords:", className="has-margin-5 has-text-weight-bold"
        )

        keywords_human = html.Div(
            ", ".join(result["keywords"]),
            className="columns is-multiline has-margin-5 has-text-weight-bold msweb-is-dimgray-txt"
        )

        if "keywords_ML" in result:
            keywords_key = "keywords_ML"
        elif "keywords_ml" in result:
            keywords_key = "keywords_ml"
        else:
            keywords_key = "keywords_ml"
            result["keywords_ml"] = []

        if len(result[keywords_key]):
            keywords_ML_label = html.Div(
                "NLP-generated keywords:", className="has-margin-5 has-text-weight-bold"
            )

            keywords_ML = html.Div(
                ", ".join(result["keywords_ML"][0:10])[0:300] + "...",
                className="columns is-multiline has-margin-5 has-text-weight-bold msweb-is-dimgray-txt"
            )

            paper_div = html.Div(
                [title,
                 authors_journal_and_year,
                 abstract,
                 summary_label,
                 summary,
                 keywords_human_label,
                 keywords_human,
                 keywords_ML_label,
                 keywords_ML],
                className="has-margin-10",
            )

        else:
            paper_div = html.Div(
                [title,
                 authors_journal_and_year,
                 abstract,
                 summary_label,
                 summary,
                 keywords_human_label,
                 keywords_human],
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

        # If url with params is too long, delete the abstract
        if len(gf_link_prefilled + urlencode(params)) > 2048:
            del params[gf_link_parameters["abstract"]]

        summary = html.A("Submit a summary for this article (or help fix a bad abstract).",
                         href=gf_link_prefilled + urlencode(params),
                         target="_blank",
                         className="a has-margin-10 msweb-is-red-link ")

        if "keywords_ML" in result and len(result["keywords_ML"]):
            keywords_ML_label = html.Div(
                "NLP-generated keywords:", className="has-margin-5 has-text-weight-bold"
            )

            keywords_ML = html.Div(
                ", ".join(result["keywords_ML"])[0:300] + "...",
                className="columns is-multiline has-margin-5 has-text-weight-bold msweb-is-dimgray-txt"
            )

            paper_div = html.Div(
                [title, authors_journal_and_year, abstract, summary_label, summary,
                 keywords_ML_label, keywords_ML],
                className="has-margin-10",
            )

        else:
            paper_div = html.Div(
                [title, authors_journal_and_year, abstract, summary_label, summary],
                className="has-margin-10",
            )

    table_cell = html.Td(paper_div)
    return html.Tr(table_cell)

    # show_similar_abstracts_button = html.Div(
    #     html.Details(
    #         [
    #             html.Summary(
    #                 html.Div("SUGGEST RELATED PRESENTATIONS",
    #                          className="button is-link has-text-weight-bold has-margin-10")
    #             ),
    #             format_similar_abstracts(result)
    #         ],
    #     ),
