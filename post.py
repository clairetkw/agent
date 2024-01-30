# from facebook import GraphAPI
import os
from dotenv import load_dotenv
import json
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.pagepost import PagePost
from facebook_business.session import FacebookSession
from facebook_business.api import FacebookRequest, FacebookAdsApi



def start_session(access_token=None):
    """Returns an API instance to make API calls."""
    # Create session and API instance
    session = FacebookSession(access_token=access_token)
    return FacebookAdsApi(session=session)


def get_app_token():
    """Returns the App Access Token"""
    api = start_session()
    node_id = "oauth"
    endpoint = "access_token"
    request = FacebookRequest(node_id, "GET", endpoint, api=api)
    params = {
        "client_id": os.environ["APP_ID"],
        "client_secret": os.environ["APP_SECRET"],
        "grant_type": "client_credentials"
    }
    request.add_params(params)

    try:
        # Execute the GET request
        response = request.execute()

        # Access the response data
        json_data = response.json()
        # http_status = response.status()
        # headers = response.headers()

        # Process the response data as needed
        # print(f"JSON Data: {json_data}")
        # print(f"HTTP Status: {http_status}")
        # print(f"Headers: {headers}")

        return json_data["access_token"]

    except Exception as e:
        # Handle any exceptions that may occur
        print(f"Error: {e}")
        return None


def get_user_id(app_id, app_token):
    """Returns the user id"""
    api = start_session(access_token=app_token)
    roles_connection = FacebookRequest(app_id, "GET", "roles", api=api)
    new_response = roles_connection.execute().json()
    return new_response["data"][0]["user"]


def get_page_token(user_token):
    """Returns Page Access Token"""
    api = start_session(access_token=user_token)
    roles_connection = FacebookRequest("me", "GET", "accounts", api=api)
    new_response = roles_connection.execute().json()
    return new_response["data"][0]["access_token"]


def get_metadata(access_token):
    """Returns the metadata of object with `access_token`."""
    api = start_session(access_token=access_token)
    request = FacebookRequest("me", "GET", "", api=api)
    request.add_param("metadata", 1)
    new_response = request.execute().json()
    return new_response


def post_to_page(message: str):
    """Writes `message` to a Facebook page. The page is referred to using the `page_token`."""
    page_token = get_page_token(os.environ["USER_TOKEN"]) 
    api = start_session(access_token=page_token)
    request = FacebookRequest("me", "POST", "feed", api=api)
    request.add_param("message", message)
    response = request.execute()
    print(response.json())

# app_token = get_app_token(api)
# print(app_token)

# page_token = get_page_token(os.environ["USER_TOKEN"])       # Seems like User Access Token must be generated manually from the explorer tool
# print(page_token)

# metadata = get_metadata(page_token)
# print(json.dumps(metadata, indent=4))

load_dotenv()
post_to_page("Hi")

# user_id = get_user_id(os.environ["APP_ID"], app_token)
# print(user_id)





# api = FacebookAdsApi.init(app_id=os.environ["APP_ID"], app_secret=os.environ["APP_SECRET"])

# fields = [
# ]
# params = {
#   'message': 'This is a test value',
# }
# print Page(id).create_feed(
#   fields=fields,
#   params=params,
# )

# def post_to_FB(message: str):
#     """Writes `message` to a Facebook page. The page is referred to using the PAGE_ACCESS_TOKEN."""
#     graph = GraphAPI(access_token=os.environ['PAGE_ACCESS_TOKEN'])
#     graph.put_object(parent_object='me', connection_name='feed', message=message)

