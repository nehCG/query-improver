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

    # top-10
    top10_res = function.query_result(service, query, google_engine_id)

    # if fewer than 10 search results, program terminate
    if (len(top10_res) < 10):
        print("There are fewer than 10 search results retrieved. Program terminated.")
        return

    # start point
    display.start(google_api_key, google_engine_id, query, precision)

    # start iteration
    while True:
        top10_res, rel_count = function.user_interface(top10_res)

        # calculate the current iteration precision
        curr_precision = float(rel_count / 10)

        # if target value for precision reached, program terminate
        if (curr_precision >= float(precision)):
            display.precision_reached(curr_precision, query)
            return

        # if there are no relevant results among the top-10 pages in the first iteration, program will terminate
        if (curr_precision == 0):
            print("There are no relevant results among the top-10 pages that Google returns. Program terminated")
            return