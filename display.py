def start(client_key, engine_key, query, precision):
    """ Function to display initial parameters to users

    Parameters:
    client_key: Google Custom Search JSON API Key
    engine_key: Google Custom Search Engine ID
    query: a list of words in double quotes
    precision: the target value for precision@10, a real number between 0 and 1

    """

    print("Parameters:")
    print("Client key  = " + client_key)
    print("Engine key  = " + engine_key)
    print("Query       = " + query)
    print("Precision   = " + precision)
    print("Google Search Results:")
    print("======================")


def each_result(count, url, title, summary):
    """Function to present each top-10 result to the user
    
    Prameters:
    count: the sequence number of result
    url: formatted URL of the result
    title: title of the result
    summary: summary of the result

    """

    print("Result", count)
    print("[")
    print(" URL:", url)
    print(" Title:", title)
    print(" Summary:", summary)
    print("]")
    print("")


def precision_reached(curr_precision, query):
    """Function to display feedback summary when desired precision reached

    Parameters:
    curr_precision: current iteration precision
    query: a list of words in current iteration query

    """

    print("======================")
    print("FEEDBACK SUMMARY")
    print("Query " + query)
    print("Precision " + str(curr_precision))
    print("Desired precision reached, done")


def iter_conclusion(query, curr_precision, precision, top_two_words):
    """Function to display iteration conclusion when desired precision is not reached

    Parameters:
    query: a list of words in current iteration query
    curr_precision: current iteration precision
    precision: the target value for precision@10, a real number between 0 and 1
    top_two_words: a list contains top two words with highest weights, using for our next query

    """
    
    print("======================")
    print("FEEDBACK SUMMARY")
    print("Query " + query)
    print("Precision " + str (curr_precision))
    print("Still below the desired precision of " + str(precision))
    print("Indexing results ....")
    print("Indexing results ....")
    print("Augmenting by  " + top_two_words[0] + " " + top_two_words[1])