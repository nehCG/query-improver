def start(client_key, engine_key, query, precision):
    print("Parameters:")
    print("Client key  = " + client_key)
    print("Engine key  = " + engine_key)
    print("Query       = " + query)
    print("Precision   = " + precision)
    print("Google Search Results:")
    print("======================")

def each_result(count, url, title, summary):
    print("Result", count)
    print("[")
    print(" URL:", url)
    print(" Title:", title)
    print(" Summary:", summary)
    print("]")
    print("")

def precision_reached(curr_precision, query):
    print("======================")
    print("FEEDBACK SUMMARY")
    print("Query " + query)
    print("Precision " + str(curr_precision))
    print("Desired precision reached, done")