'''
===============
Here we make the AI respond as per a BaseClass: structured outputs and validation checks
===============
'''

from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
openai = OpenAI()

class Evaluation(BaseModel):
   is_acceptable: bool
   feedback: str

question = "what is 2+2?"

response = openai.chat.completions.parse(
    model = "gpt-4o-mini",
    messages = [
        {"role": "system", "content": question}, 
        {"role": "user", "content": "answer the question" }
        ],

    response_format=Evaluation,
)

reply = response.choices[0].message.parsed
print(reply.is_acceptable)
print(reply.feedback)

# check for creation of Pydantic object, if you remove any one arg, it raises an error
ev = Evaluation(is_acceptable=True, feedback="sucess")
print(ev)