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


def rel_rocchio_algo(query_words_weights, rel_info_dict_weights,
                     nrel_info_dict, rel_info_dict, rel_info_df, rel_res_list):
    """Function to apply rocchio algorithm to relevant results, updating query_words_weights

    Parameters:
    query_words_weights: a dictionary stores current query words and corresponding weights
    rel_info_dict_weights: a dictionary stores relevant info where the keys are words and the values are weights
    nrel_info_dict: a dict stores non-relevant info
    rel_info_dict: a dict stores relevant info
    rel_info_df: a dictionary stores relevant info where the keys are words and the values are document frequency
    rel_res_list: a list includes all relevant results

    Returns:
    query_words_weights: a dictionary stores query words and corresponding weights, updated by relevant results

    """

    alpha, beta = 1, 0.75

    for term in rel_info_dict:
        if term in nrel_info_dict:
            inverse_doc_freq = math.log10(10 / (float(len(rel_info_dict[term]) + len(nrel_info_dict[term]))))
        else:
            inverse_doc_freq = math.log10(10 / float(len(rel_info_dict[term])))

        rel_info_dict_weights[term] += beta * inverse_doc_freq * (len(rel_info_dict[term]) * float(rel_info_df[term]) / len(rel_res_list))
            
        if term in query_words_weights:
            query_words_weights[term] = alpha * query_words_weights[term] + rel_info_dict_weights[term]
        elif rel_info_dict_weights[term] > 0:
            query_words_weights[term] = rel_info_dict_weights[term]

    return query_words_weights


def nrel_rocchio_algo(query_words_weights, nrel_info_dict_weights,
                      rel_info_dict, nrel_info_dict, nrel_info_df, nrel_res_list):
    """Function to apply rocchio algorithm to non-relevant results, updating query_words_weights

    Parameters:
    query_words_weights: a dictionary stores updated query words and corresponding weights
    nrel_info_dict_weights: a dictionary stores non-relevant info where the keys are words and the values are weights
    rel_info_dict: a dict stores relevant info
    nrel_info_dict: a dict stores non-relevant info
    nrel_info_df: a dictionary stores non-relevant info where the keys are words and the values are document frequency
    nrel_res_list: a list includes all non-relevant results

    Returns:
    query_words_weights: a dictionary stores query words and corresponding weights, updated by non-relevant results

    """

    alpha, gamma = 1, 0.15

    for term in nrel_info_dict:
        if term in rel_info_dict:
            inverse_doc_freq = math.log10(10 / (float(len(nrel_info_dict[term]) + len(rel_info_dict[term]))))
        else:
            inverse_doc_freq = math.log10(10 / float(len(nrel_info_dict[term])))

        nrel_info_dict_weights[term] -= gamma * inverse_doc_freq * (len(nrel_info_dict[term]) * float(nrel_info_df[term]) / len(nrel_res_list))
            
        if term in query_words_weights:
            query_words_weights[term] = alpha * query_words_weights[term] + nrel_info_dict_weights[term]
        elif nrel_info_dict_weights[term] > 0:
            query_words_weights[term] = nrel_info_dict_weights[term]

    return query_words_weights


def get_new_words(sorted_tuple_list, query_words_list):
    """ Function to get two new words from sorted tuple list

    Parameters:
    sorted_tuple_list: a sorted tuple list contains (word, weight), descending order by weight
    query_words_list: current query list

    Returns:
    two_new_words: a list contains top two words with highest weights, using for our next query
    
    """

    two_new_words = []
    for t in sorted_tuple_list:
        if t[0].lower() not in query_words_list:
            two_new_words.append(t[0].lower())
        if len(two_new_words) == 2:
            break
    return two_new_words


def order_new_words(two_new_words):
    """Function to order two new words

    Parameters:
    two_new_words: a list contains top two words with highest weights, using for our next query

    Returns:
    two_new_words: a updated list contains top two words with highest weights, using for our next query

    """
    
    if len(two_new_words[0]) < len(two_new_words[1]):
        two_new_words[0], two_new_words[1] = two_new_words[1], two_new_words[0]
    
    return two_new_words