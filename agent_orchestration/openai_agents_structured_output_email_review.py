"""
============
Structured Outputs
============
"""

import os
from dotenv import load_dotenv
from agents import Agent, Runner, trace
import asyncio
from pydantic import BaseModel, Field

# load the api key
load_dotenv(override=True)


# create the class for structured output so that the AI outputs the included variables
class EmailReview(BaseModel):
    is_professional:bool       = Field(description="whether the email is pro and appropriate?")
    number_of_sentences: int   = Field(description="number of sentences in body of email, not including the greeting and signature")
    contains_placeholders:bool = Field(description="whether the email contains placeholders for personalization")   
    

# returns a python dict representing the JSONs schema of the class EmailReview
print(EmailReview.model_json_schema())


email = """
Hi Mayank,
I'm hitting you up to see if you'd like to buy our product. It's really great. You'll miss out if you don't buy it.
Ed
"""

agent1 = Agent(
    name = "checker",
    instructions= "you review the email",
    model = "gpt-4o-mini",
    output_type = EmailReview # this is where the output is defined as structured outputs
)


async def main():
    with trace("structured outputs"):
        results = await Runner.run(agent1, email)
        print(results.final_output)
    
    
    
if __name__ == "__main__":
    asyncio.run(main())