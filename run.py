import function
import display


def search(google_api_key, google_engine_id, precision, query):

    # Build a service object for interacting with the API
    service = function.build_service(google_api_key)

    # top-10
    top10_res = function.query_result(service, query, google_engine_id)

    # if fewer than 10 search results, program terminate
    if (len(top10_res.get('items')) < 10):
        print("There are fewer than 10 search results retrieved. Program terminated.")
        return

    # start point
    display.start(google_api_key, google_engine_id, query, precision)

    # start iteration
    while True:
        count = 1   
        rel_count = 0 
        
        rel_info_list = []
        nrel_info_list = []

        for r in top10_res.get('items'):    
            title = r.get('title')
            url = r.get('formattedUrl')
            summary = r.get('snippet')

            # present top-10
            display.each_result(count, url, title, summary)

            # mark each
            rel_count, rel_info_list, nrel_info_list = function.user_interface(rel_count, rel_info_list, nrel_info_list, title, summary)

            count += 1

        curr_precision = rel_count / (count - 1)

        # if target value for precision reached, program terminate
        if (curr_precision >= float(precision)):
            display.precision_reached(curr_precision, query)
            return

        # if there are no relevant results among the top-10 pages in the first iteration, program terminate
        if (curr_precision == 0):
            print("There are no relevant results among the top-10 pages that Google returns. Program terminated")
            return