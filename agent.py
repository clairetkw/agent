import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import time
import requests
from post import post_to_FB
#from transformers import pipeline

load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

# Set up Hugging Face summarization pipeline
#summarizer = pipeline("summarization")

def get_interior_design_trends(location="Singapore", BING_API_KEY=os.getenv('BING_API_KEY')):
    start_time_function = time.time()
    # Define the base URL for Bing Web Search API
    api_url = "https://api.bing.microsoft.com/v7.0/search"

    # Define the query to search for interior design trends
    query = f"Most reliable interior designer companies {location}"

    # Set up headers for the API request
    headers = {
        "Ocp-Apim-Subscription-Key": BING_API_KEY,
    }

    # Set up parameters for the API request
    params = {
        "q": query,
        "count": 50,  # Number of results to retrieve (adjust as needed)
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

tools_list = [{
  "type": "function",
    "function": {
      "name": "get_interior_design_trends",
      "description": "Get the top 5 most reliable interior designer companies in Singapore. Provide reasons for choosing these companies.",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {"type": "string", "description": "Singapore"}
        },
        "required": ["location"]
      }
    }
}]

#create assistant (only need to do this ONCE)
my_assistant = client.beta.assistants.create(
    name="Test3 Interior Design Expert",
    instructions="You are an interior design expert in Singapore. Conduct research online to answer questions.",
     model="gpt-4",
     tools=tools_list
)
#print(my_assistant.model_dump_json(indent=2))

start_time = time.time()

#create thread
empty_thread = client.beta.threads.create()

#create message to add to thread
thread_message = client.beta.threads.messages.create(
    empty_thread.id,
    role="user",
    content="Who are the top 5 interior most reliable interior designer companies in Singapore?"
)
#print(thread_message.model_dump_json(indent=2))

# run assistant
run = client.beta.threads.runs.create(
  thread_id=empty_thread.id,
  assistant_id=my_assistant.id
)
#print(run.model_dump_json(indent=2))

while True:
  #retrieve status of the run
  run_status = client.beta.threads.runs.retrieve(thread_id=empty_thread.id,
  run_id=run.id)

  print(f"Run status: {run_status.status}")
  if run_status.status == 'completed':
    messages = client.beta.threads.messages.list(
      thread_id = empty_thread.id
    )
    for msg in messages.data:
      role = msg.role
      content = msg.content[0].text.value
      print(f"{role.capitalize()}: {content}")
      post_to_FB(content)
      break
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Time taken: {time_taken} seconds")
    break

  elif run_status.status == 'requires_action':
    print("Requires action")
    required_actions = run_status.required_action.submit_tool_outputs.model_dump()
    print(required_actions)
    tools_output = []
    for action in required_actions["tool_calls"]:
        func_name = action["function"]["name"]
        arguments = json.loads(action["function"]["arguments"])
        if func_name == "get_interior_design_trends":
            output = get_interior_design_trends(location=arguments["location"])
            tools_output.append({
                "tool_call_id": action["id"],
                "output": json.dumps(output)  # Convert output to a JSON string
            })
        else:
            print("Function not found")
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=empty_thread.id,
        run_id=run.id,
        tool_outputs=tools_output
    )
time.sleep(1) # Wait for a second before checking again

# messages = client.beta.threads.messages.list(
#   thread_id=empty_thread.id
# )

# assistant_response = messages.data[0].content[0].text.value


# print(assistant_response)
