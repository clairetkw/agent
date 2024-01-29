import json
import os
from openai import OpenAI
from crewai import Agent, Task, Crew, Process
from langchain.tools import tool
from dotenv import load_dotenv
import requests
import time

load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

@tool
def get_interior_design_trends(location="Singapore", BING_API_KEY=os.getenv('BING_API_KEY')):
    """
    Get the interior design trends based on the Bing Web Search API.

    Args:
        location (str): The location for which trends are to be retrieved.
        BING_API_KEY (str): The API key for the Bing Web Search API.

    Returns:
        dict: A dictionary containing the location and trends information.
    """
    start_time_function = time.time()
    # Define the base URL for Bing Web Search API
    api_url = "https://api.bing.microsoft.com/v7.0/search"

    # Define the query to search for interior design trends
    query = f"Interior design trends {location}"

    # Set up headers for the API request
    headers = {
        "Ocp-Apim-Subscription-Key": BING_API_KEY,
    }

    # Set up parameters for the API request
    params = {
        "q": query,
        "count": 5,  # Number of results to retrieve (adjust as needed)
        "offset": 0,
        "safeSearch": "Moderate",  # Adjust as needed
    }

    # Make a GET request to the Bing Web Search API
    response = requests.get(api_url, headers=headers, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON content of the response
        data = response.json()

        # Extract relevant information from the response
        trends = []

        # Use OpenAI API to pass results to assistant
        for item in data.get("webPages", {}).get("value", []):
            content = item.get("snippet", "")  # You can use "name" or other fields based on API response
            trends.append(content)
        end_time_function = time.time()
        time_taken_function = end_time_function - start_time_function
        print(f"Time taken for function (success): {time_taken_function} seconds")
        return {"location": location, "trends": trends}
    else:
      error_message = f"Failed to retrieve interior design trends. Status code: {response.status_code}"
      try:
          error_content = response.json()
          error_message += f", Error content: {error_content}"
      except json.JSONDecodeError:
        pass  # Ignore if response content is not JSON
      end_time_function = time.time()
      time_taken_function = end_time_function - start_time_function
      print(f"Time taken for function (failed): {time_taken_function} seconds")
      return {"error": error_message}
    
search_tool = get_interior_design_trends

# Define your agents with roles and goals
researcher = Agent(
  role='CrewAI Interior Design Expert',
  goal='Uncover the latest trends in interior design in Singapore',
  backstory="""You are an interior design expert in Singapore. Conduct research online to answer questions.""",
  verbose=True,
  allow_delegation=False,
  tools=[search_tool]
)

# Create tasks for your agents
task1 = Task(
  description="""Get the interior design trends in Singapore. Do not include the names of any specific interior designers.
  Your final answer MUST be a list of 5 interior design trends.""",
  agent=researcher
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher],
  tasks=[task1],
  verbose=2, # You can set it to 1 or 2 to different logging levels
)

start_time = time.time()
# Get your crew to work!
result = crew.kickoff()
end_time = time.time()

print("######################")
time_taken = end_time - start_time
print(f"Time taken: {time_taken} seconds")
print(result)