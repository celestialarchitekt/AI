''' 
========================
This exercise involves:
1. getting an api key and storing it in a .env file
2. accessing the api key 
3. creating messages and using chat.completions API to ask the model
4. using Markdown if needed
========================
'''


import os
from dotenv import load_dotenv
load_dotenv(override=True)


open_api_key = os.getenv('OPENAI_API_KEY')

if open_api_key:
    print(f"key found and begins with {open_api_key[:10]}")
else:
    print(f"key not found ")


'''
open_api_key = os.environ['OPENAI_API_KEY']
print(open_api_key)
'''

'''
for key,value in os.environ.items():
    print(key,":",value)
'''

from openai import OpenAI
openai = OpenAI()

# create list of messages 
messages = [{"role": "user", "content": "what is 2+2?"}]

# call OpenAI model with the message
response = openai.chat.completions.create(
    model = "gpt-4.1-nano",
    messages=messages
)

print(response.choices[0].message.content)

#Ask a question
question = "Which is the most famous book from Sri Aurobindo?"
messages = [{"role": "user", "content": question}]

# call OpenAI with the question
response = openai.chat.completions.create(
    model = "gpt-4.1-nano",
    messages=messages
)

answer = response.choices[0].message.content
#print(answer)

# markdown
from IPython.display import Markdown, display
md_object = Markdown(answer)
raw_text = md_object.data
print(raw_text)