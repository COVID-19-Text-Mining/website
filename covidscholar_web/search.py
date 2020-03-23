import pymongo
import time
import os
from datetime import timedelta
import datetime
import requests
import json


from covidscholar_web.constants import max_results

client = pymongo.MongoClient(host=os.getenv('COVID_HOST'),
                             username=os.getenv('COVID_USER'),
                             password=os.getenv('COVID_PASS'),
                             authSource=os.getenv('COVID_DB'))
db = client[os.getenv('COVID_DB')]


def search_abstracts(text, limit=max_results):
    """
    Search the database

    Inputs:
            text (str): text to search. Searches both entities and text matches
            limit (int): number of abstracts to return.

    Returns:
            Dict with keys:
                Exact Matches
                Partial Matches
    """

    response = requests.post(os.environ["COVID_API_ENDPOINT"] + "/search/", data={"text": text, "limit": limit})
    return_dict = json.loads(response.text)
    return return_dict

def get_all(limit=max_results):
    """
    Return all submissions.

    """
    response = requests.get(os.environ["COVID_API_ENDPOINT"] + "/submissions")
    print(response)
    return_dict = json.loads(response.text)
    return return_dict


