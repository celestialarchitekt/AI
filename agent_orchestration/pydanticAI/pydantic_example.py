"""
=======
PydanticAI - a simple example
=======
"""

import os
import asyncio
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from dotenv import load_dotenv

# load api keys, os.getenv("name")
api_keys=load_dotenv(override=True) # bool object

# check API
if api_keys:
    print("API keys loaded")


# define the class for LLM output
class CityFact(BaseModel):
    city: str
    country: str
    fun_fact: str


# create the model
model = OpenAIResponsesModel("gpt-4o-mini")

# create the agent
agent_finance = Agent(
    model = model,
    output_type = CityFact,
    system_prompt = "You are an ai agent, that gives info on financial markets"
)


# main function
async def main():
    prompt = "give 2027 eu financial market"

    result = await agent_finance.run(prompt)

    # print output
    print("\n" + "-"*100 + "\n")
    print(result.output)
    


# call to main
if __name__ == "__main__":
    asyncio.run(main())