import pymongo
import time
import os
from datetime import timedelta
import datetime
import requests
import json

from covidscholar_web.constants import max_results


def search_abstracts(text, limit=30, collection="entries", covid19_only=False):
    """
    Search the database

    Inputs:
            text (str): text to search. Searches both entities and text matches
            limit (int): number of abstracts to return.
            collection (str): "entries"(google form data) or "search"(scraped data)
    Returns:
            Dict with keys:
                Exact Matches
                Partial Matches
    """

    response = requests.post(os.environ["COVID_API_ENDPOINT"] + f"/{collection}/",
                             params={"text": text, "limit": limit, "covid19_only": covid19_only})
    return_dict = json.loads(response.text)
    return return_dict


def get_all(limit=max_results):
    """
    Return all submissions.

    """
    response = requests.get(os.environ["COVID_API_ENDPOINT"] + "/submissions")
    return_dict = json.loads(response.text)
    return return_dict


def most_recent():
    """
    Return the most recent submissions.

    """
    response = requests.get(os.environ["COVID_API_ENDPOINT"] + "/recent/")
    return_dict = json.loads(response.text)
    print(os.environ["COVID_API_ENDPOINT"] + "/recent")
    return return_dict
