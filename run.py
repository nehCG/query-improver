import function
import display


def search(google_api_key, google_engine_id, precision, query):
    """Function to start searching using user-iput query and precision, will terminate until desired result obtained.

    Parameters:
    google_api_key: Google Custom Search JSON API Key
    google_engine_id: Google Custom Search Engine ID
    precision: the target value for precision@10, a real number between 0 and 1
    query: a list of words in double quotes (e.g., “Milky Way”)

    """

    # Build a service object for interacting with the API
    service = function.build_service(google_api_key)

    # retrieve the top-10 results for the query from Google
    top10_res = function.query_result(service, query, google_engine_id)

    # if fewer than 10 search results retrieved in the first iteration, program will terminate
    if (len(top10_res) < 10):
        print("There are fewer than 10 search results retrieved. Program terminated.")
        return

    # start point, display general parameters to users
    display.start(google_api_key, google_engine_id, query, precision)

    # iteration starts, terminate when desired precision reached
    while True:
        
        rel_res_list = []   # create a list to store relecant results
        nrel_res_list = []  # create a list to sotre non-relevant results

        # pop up a user interface that let user to determine whether the result is relevant or not
        # then update results to corresponding list
        rel_res_list, nrel_res_list = function.user_interface(top10_res, rel_res_list, nrel_res_list)

        # calculate the current iteration precision
        curr_precision = len(rel_res_list) / 10

        # if target value for precision reached, program terminate
        if (curr_precision >= float(precision)):
            display.precision_reached(curr_precision, query)
            return

        # if there are no relevant results among the top-10 pages in the first iteration, program will terminate
        if (curr_precision == 0):
            print("There are no relevant results among the top-10 pages that Google returns. Program terminated")
            return
        
        # calculate the document frequency of tokens in a list of search results, then update to result lists
        rel_info_dict, rel_res_list = function.get_doc_freq(rel_res_list)
        nrel_info_dict, nrel_res_list = function.get_doc_freq(nrel_res_list)

        # create a list to keep tracking words in our query
        query_words_list = []
        query_words_list = ''.join(query.lower()).split()

        # create a dictionary to store current query words and corresponding weights
        query_words_weights = {word: 1.0 for word in query_words_list}

        # process document frequency to get parameters for using rocchio algorithm
        rel_info_dict_weights, rel_info_df = function.process_doc_freq(rel_info_dict, rel_res_list)
        nrel_info_dict_weights, nrel_info_df = function.process_doc_freq(nrel_info_dict, nrel_res_list)

        # apply rocchio algorithm to relevant results, updating query_words_weights
        query_words_weights = function.rel_rocchio_algo(query_words_weights, rel_info_dict_weights,
                                                        nrel_info_dict, rel_info_dict, rel_info_df, rel_res_list)
        
        # apply rocchio algorithm to non-relevant results, updating query_words_weights
        query_words_weights = function.nrel_rocchio_algo(query_words_weights, nrel_info_dict_weights,
                                                         rel_info_dict, nrel_info_dict, nrel_info_df, nrel_res_list)

        # sort query_words_weights dictionary by weights with descending order       
        sorted_tuple_list = sorted(query_words_weights.items(), key=lambda x:x[1], reverse=True)

        # get top two new words from the sorted tuple list
        two_new_words = function.get_new_words(sorted_tuple_list, query_words_list)

        # order two new words
        two_new_words = function.order_new_words(two_new_words)

        # display iteration conclusion when desired precision is not reached
        display.iter_conclusion(query, curr_precision, precision, two_new_words)

        # update query, add two retrieved new words
        query += " " + two_new_words[0] + " " + two_new_words[1]

        # new iteration start point, display general parameters to users
        display.start(google_api_key, google_engine_id, query, precision)

        # retrieve the top-10 results for the new query from Google
        top10_res = function.query_result(service, query, google_engine_id)