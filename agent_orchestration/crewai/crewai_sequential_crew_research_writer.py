"""
===========

CrewAI - is an orchestration framework, built on top of langchain to orchestrate autonomous agents to work together like a team.
In this example, there is no master agent, but the tasks are executed sequentially.
==========
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process


load_dotenv(override=True)

# Define Agents
researcher = Agent(
    role = "technology researcher",
    goal = "uncover cutting-edge in ai and technology",
    backstory = "you are veteran technology anaylst at a leading tech publication. \
        You excel at identifying trends, summarizing complex topics, and identifying key takeaways.",

    verbose=True,
    memory=True,
    llm = "gpt-5.4-mini"
)

writer = Agent(
    role ="tech content strategist",
    goal = "craft compelling content on tech advancements",
    backstory = "you are a skilled writer known for converting complex technical research into engaging, easy to understand articles.",
    verbose=True,
    memory=True,
     llm = "gpt-5.4-mini"
)


# Define Tasks
research_task = Task(
    description = "analyze the key advantages of using multi agent systems in software dev",
    expected_output = "a bulleted list of top 3-5 advantages with concise explanation",
    agent = researcher
)


writer_task=Task(
    description = "using the research output provided, write an engaging 2 paragraph blog",
    expected_output= "a polished 2 paragraph blog post",
    agent = writer
)


# KickOff Crew
tech_crew = Crew(
    agents = [researcher, writer],
    tasks = [research_task, writer_task],
    process = Process.sequential, # executes tasks sequentially
    verbose=True

)


# kickoff

result = tech_crew.kickoff()

print(result)