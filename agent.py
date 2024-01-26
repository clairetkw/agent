import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import time


start_time = time.time()

load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

#create assistant (only need to do this ONCE)
# my_assistant = client.beta.assistants.create(
#     name="Test Interior Design Expert",
#     instructions="You are an interior design expert in Singapore. Conduct research online to answer questions.",
#      model="gpt-4",
#      tools=[{
#       "type": "function",
#     "function": {
#       "name": "getInteriorDesignTrends",
#       "description": "Get the interior design trends in Singapore",
#       "parameters": {
#         "type": "object",
#         "properties": {
#           "location": {"type": "string", "description": "Singapore"},
#           "unit": {"type": "string", "enum": ["c", "f"]}
#         }
#       }
#     }
#   }]
# )
# print(my_assistant.model_dump_json(indent=2))

#create thread
empty_thread = client.beta.threads.create()

thread_message = client.beta.threads.messages.create(
    empty_thread.id,
    role="user",
    content="What are the top interior design trends in Singapore?"
)
#print(thread_message.model_dump_json(indent=2))

# run query
run = client.beta.threads.runs.create(
  thread_id=empty_thread.id,
  assistant_id="asst_1NRfOoC6YMCZVsDHXCZtIvor",
  instructions="Please address the user as Jane Doe. The user has a premium account.",
)
#print(run.model_dump_json(indent=2))

while True:
  run_status = client.beta.threads.runs.retrieve(thread_id=empty_thread.id,
  run_id=run.id)

  print(f"Run status: {run_status.status}")

  if run_status.status == 'requires_action':
    print("Requires action")
    required_actions = run_status.required_action.submit_tool_outputs.model_dump()
    print(required_actions)
    tools_output = []
    for action in required_actions["tool_calls"]:
      func_name = action["function"]["name"]
      arguments = json.Loads(action["function"]["arguments"])
      if func_name == "getInteriorDesignTrends":
        output = getInteriorDesignTrends(arguments["Singapore"])
        tools_output.append({
          "id": action["id"],
          "output": output
        })
      else:
        print("Function not found")
    client.beta.threads.runs.submit_tool_outputs(
      thread_id=empty_thread.id,
      run_id=run.id,
      tool_outputs=tools_output
    )
    
  elif run_status.status == 'completed':
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Time taken: {time_taken} seconds")
    break
time.sleep(1) # Wait for a second before checking again

messages = client.beta.threads.messages.list(
  thread_id=empty_thread.id
)

assistant_response = messages.data[0].content[0].text.value


print(assistant_response)
