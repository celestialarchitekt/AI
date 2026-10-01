"""
_________________________________________________
Creating several agents:
1. Search agent - search the web 
2. Planner agent - plans the task 
3. Writer agent - writes report 
4. Notification agent - sends push notification
________________________________________________
"""

#region imports
import os
import asyncio
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from agents import Agent, trace, Runner, function_tool, WebSearchTool
#endregion


#region load env vars and constants
load_dotenv(override=True)

MODEL_NAME = "gpt-4o-mini"
HOW_MANY_SEARCHES = 3

pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user  = os.getenv("PUSHOVER_USER")
pushover_url   = "https://api.pushover.net/1/messages.json"

if pushover_token:
    print(f"found pushover token with {pushover_token[:5]}")
else:
    print("pushover token not found")

if pushover_user:
    print(f"found pushover user token with {pushover_user[:5]}")
else:
    print("pushover user token not found")
#endregion



#------------- 1st Agent Planner Agent
class WebSearchItem(BaseModel):
    reason:str = Field(description="your reason for why this search is important to query")
    query:str  = Field(description="the search term used for the web search")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="a list of web searches to perform")


INSTRUCTIONS_PLANNER_AGENT = f"""
you are a planner agent. given a user query, create a search strategy.
output  {HOW_MANY_SEARCHES} web search queries to gather comprehesive information.

"""


planner_agent = Agent(
    name = "planner_agent",
    instructions = INSTRUCTIONS_PLANNER_AGENT,
    model = MODEL_NAME,
    output_type = WebSearchPlan
)


#------------- 2nd Agent Search Agent
INSTRUCTIONS_SEARCH_AGENT = """
You are a research agent, given a search term, search the web for that term and produce concise summary of results.
The summary must be 2 paragraphs only and less than 300 words.
"""

search_agent = Agent(
    name = "search_agent",
    instructions = INSTRUCTIONS_SEARCH_AGENT,
    model = MODEL_NAME,
    tools = [WebSearchTool()]
)

#------------- 3rd Agent Writer Agent
INSTRUCTIONS_WRITER_AGENT= """
You are a professional writer. Given the summary generate a concise report, formatted in Markdown format.
"""

writer_agent = Agent(
    name="writer_agent",
    instructions = INSTRUCTIONS_WRITER_AGENT,
    model = MODEL_NAME,

)


#------------- 4th Agent Notification Agent
INSTRUCTIONS_NOTIFICATION_AGENT = """
You are a notifications agent, use the tool 'pushover' to send the notification.
"""

@function_tool
async def pushover(message:str)->str:
    """Sends a push notification via Pushover API."""
    print(f"\n[Push Notification Tool Fired]: {message}\n")
    
    if pushover_token and pushover_user:
        payload = {"user": pushover_user, "token": pushover_token, "message": message}
        requests.post(pushover_url, data=payload)
        return "notification sent successfully"
    

    return "pushover credentials missing; notification simulated"


notification_agent = Agent(
    name = "notification_agent",
    instructions = INSTRUCTIONS_NOTIFICATION_AGENT,
    model = MODEL_NAME,
    tools = [pushover]

)


#---------------- Orchestration Functions , 1 for each Agent
async def run_planner(user_query:str)->WebSearchPlan:
    result = await Runner.run(planner_agent, user_query)
    #print(f"Result of planner agent: {result.final_output.searches}")

    return result.final_output.searches




async def run_search(query:str)->str:
   result = await Runner.run(search_agent, query)
   #print(f"result of search agent: {result}")

   return result



async def run_writer(summaries: list[str])->str:
    # LLM agents only understand texts - strings or json, so the list needs to be converted to string type
    combined_input = "---- Summary-----".join(summaries)
    result = await Runner.run(writer_agent, combined_input)
    return result.final_output



async def run_notification(report:str)->str:
   result = await Runner.run(notification_agent, report)
   return result




#---------------- Query 

user_query = "Most efficient top rated AI Agents on HuggingFace."




#----------------- Main Function
async def main():
    #1. run the planner agent with user query
    result_planner:WebSearchPlan  = await run_planner(user_query)
    print(result_planner)

    # create an empty list
    search_results_list= []
    
    # returns a pydantic object of class WebSearchPlan with reason and query, we extact the query , all 3 of them and pass it to the next function
    for index , value in enumerate(result_planner):
        print(index)
        print(value.query)

        #2. call the function run_search with results from planner agent
        search_result = await run_search(value.query)
        #print(f"search results: {search_result.final_output}")
        search_results_list.append(search_result.final_output)
        

    #print the search_results_list - output from search agent
    print(search_results_list)
    

    #3. run the writer agent with the results from search agent
    report = await run_writer(search_results_list)
    print(f"Report is: {report}")


    #4. run the notifications Agent 
    status = await run_notification(report)

    print(status)



#----------------- Calling Main
if __name__ == "__main__":
    asyncio.run(main())