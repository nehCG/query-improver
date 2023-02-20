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


def user_interface(top10_res, rel_res_list, nrel_res_list):
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
    for res in top10_res:
        display.each_result(count, res['url'], res['title'], res['summary'])

        while True:
            user_response = input("Relevant (Y/N)?")
            if user_response.upper() == "Y":
                rel_res_list.append(res)
                break
            elif user_response.upper() == "N":
                nrel_res_list.append(res)
                break
            else:
                print("Invalid input. Please enter (Y/N).")

        count += 1

    return rel_res_list, nrel_res_list


def create_stopwords_list():
    """Function to transfer stopwords.txt file to a list"""

    stop_words = []
    with open('stopwords.txt', 'r') as f:
        for line in f:
            stop_words.append(line.strip('\n').split(',')[0])
    return stop_words


def get_doc_freq(res_list):
    """Function to calculate the document frequency of tokens in a list of search results.

    Parameters:
    re_list: a list of search results, where each search result is a dictionary 
    that contains a "title" and a "summary" field

    Returns:
    info_dict: a dictionary where the keys are the unique tokens found in the search results and the
    values are sets containing the indices of the search results where the token appears
    res_list: The list of search results with an additional "doc_freq" field in each dictionary. 
    The "doc_freq" field is a dictionary where the keys are the unique tokens found in the search result
    and the values are the number of search results that contain the token

    """

    info_dict = defaultdict(set)

    for i, res in enumerate(res_list):
        tokens = word_tokenize(res["title"] + " " + res["summary"])
        meaningful_tokens = []
        for w in tokens:
            if w.lower() not in create_stopwords_list() and len(w) > 1:
                meaningful_tokens.append(w)

        res['doc_freq'] = defaultdict(int)
        for token in set(meaningful_tokens):
            res['doc_freq'][token] = meaningful_tokens.count(token)
            info_dict[token].add(i)

    return info_dict, res_list


def process_doc_freq(info_dict, res_list):
    """Function to process document frequency to get parameters for using rocchio algorithm

    Parameters:
    info_dict: a dictionary where the keys are the unique tokens found in the search results and the
    values are sets containing the indices of the search results where the token appears
    res_list: a list of search results, where each search result is a dictionary 
    that contains a "title" and a "summary" field

    Returns:
    info_dict_weights: a dictionary where the keys are words and the values are weights
    info_df: a dictionary where the keys are words and the values are document frequency

    """

    info_dict_weights = {word: 0.0 for word in info_dict}

    info_df = {}

    for res in res_list:
        for term in res["doc_freq"]:
            info_df[term] = info_df.get(term, 0) + res["doc_freq"][term]

    return info_dict_weights, info_df


def rocchio_algo():
    return