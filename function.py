import math
import display
from googleapiclient.discovery import build
from nltk.tokenize import word_tokenize
from collections import defaultdict


def build_service(google_api_key):
    """Function to build a service object for interacting with the API

    Parameter:
    google_api_key: Google Custom Search JSON API Key

    Returns:
    a service object built base on JSON API key

    """

    service = build(
        "customsearch", "v1", developerKey = google_api_key
    )

    return service


def query_result(service, query, google_engine_id):
    """Function to retrieve the top-10 results for the query from Google

    Parameter:
    service: a service object built base on JSON API key
    query: a list of words in double quotes (e.g., “Milky Way”)
    google_engine_id: Google Custom Search Engine ID

    Returns:
    top10_res: a list includes top-10 query results

    """

    top10_res = []

    res = (
        service.cse()
        .list( 
            q = query, 
            cx = google_engine_id,
        )
        .execute()
    )

    for r in res.get("items"):
        title = r.get('title')
        url = r.get('formattedUrl')
        summary = r.get('snippet')

        each_res = {
            "title": title,
            "url": url,
            "summary": summary,
        }
        top10_res.append(each_res)

    return top10_res


def user_interface(top10_res):
    """Function to create user interface to let user mark whether each reasult is relevant or not,
    then return desired parameters.

    Parameters:
    top10_res: a list includes top-10 query results

    Returns:
    top10_res: a list includes top-10 query results and has boolean value 'rel' to represent
    whether this result is relevant or not
    rel_count: the number of relevant results determined by user
    
    """

    count = 1
    rel_count = 0
    for res in top10_res:
        res['rel'] = False
        display.each_result(count, res['url'], res['title'], res['summary'])

        user_response = input("relevant (Y/N)?")
        if user_response.upper() == "Y":
            rel_count += 1
            res['rel'] = True
        elif user_response.upper() == "N":
            res['rel'] = False
        else:
            print("Invalid input. Please enter (Y/N).")
            user_response = input("relevant (Y/N)?")

        count += 1

    return top10_res, rel_count


def create_stopwords_list():
    """Function to transfer stopwords.txt file to a list"""

    stop_words = []
    with open('stopwords.txt', 'r') as f:
        for line in f:
            stop_words.append(line.strip('\n').split(',')[0])
    return stop_words