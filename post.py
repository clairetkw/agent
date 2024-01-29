from facebook import GraphAPI
import os

def post_to_FB(message: str):
    """Writes `message` to a Facebook page. The page is referred to using the PAGE_ACCESS_TOKEN."""
    graph = GraphAPI(access_token=os.environ['PAGE_ACCESS_TOKEN'])
    graph.put_object(parent_object='me', connection_name='feed', message=message)
