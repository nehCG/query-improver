from googleapiclient.discovery import build


def build_service(google_api_key):

    service = build(
        "customsearch", "v1", developerKey = google_api_key
    )

    return service


def query_result(service, query, google_engine_id):

    res = (
        service.cse()
        .list( 
            q = query, 
            cx = google_engine_id,
        )
        .execute()
    )
    return res


def user_interface(rel_count, rel_info_list, nrel_info_list, title, summary):

    while True:
        user_response = input("Relevant (Y/N)?")

        if user_response.upper() == "Y":
            rel_count += 1
            rel_info_list.append(title + " " + summary)
            break
        elif user_response.upper() == "N":
            nrel_info_list.append(title + " " + summary)
            break
        else:
            print("Invalid input. Please enter (Y/N).")

    return rel_count, rel_info_list, nrel_info_list