'''
================================
Introducing TOOLS with AgenticAI
================================
'''

import sys
from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)
openai = OpenAI()

pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_url = "https://api.pushover.net/1/messages.json"

if pushover_token:
    print(f"found pushover token with {pushover_token[:5]}")
else:
    print("pushover token not found")

if pushover_user:
    print(f"found pushover user token with {pushover_user[:5]}")
else:
    print("pushover user token not found")



# Push Function to send notification
def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)


# Functions for Pushover Notifications
def record_user_details(email, name="not provided", notes="not provided"):
    push(f"Recording interest from {name} with {email} and notes {notes}")
    return {"recorded": "ok"}


def record_unknown_question(question):
    push(f"recording {question} asked that I could not answer")
    return {"recorded": "ok"}


# Tools
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}


record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}



# Tool List
tools = [{"type": "function", "function": record_user_details_json},
         {"type": "function", "function": record_unknown_question_json}
        ]



# Function to run Tools, iterate through tools and run specific tools
def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
       
        #OpenAI returns JSON, this gets converted into dictionaries (arguments)
        arguments = json.loads(tool_call.function.arguments) 
        print(f"tool called: {tool_name}", flush=True)

        if tool_name == "record_user_details":
            # ** unpacks the dictionary key,value pair
            result = record_user_details(**arguments)
        elif tool_name == "record_unknown_question":
            result = record_unknown_question(**arguments)

        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})

    return results



# Pypdf
reader = PdfReader("cv.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin+=text


# Summary
with open("summary.txt", "r", encoding="utf-8") as f:
    summary=f.read()


# Name
name = "MJ"


# System Prompt
system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website. \
                particularly questions related to {name}'s career, background, skills and experience. \
                Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
                You are given summary of {name}'s background and LinekdIn profile which you can use to answer questions. \
                If you dont know the answer to any questions, use your record_unknown_question tool to record the question that you could not answer. \
                If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool."


system_prompt += f"\n Summary: {summary}"
system_prompt += f"\n LinkedIn: {linkedin}"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."



# Chat Message; LLM call is in here
def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    done = False

    while not done:
        response = openai.chat.completions.create(
            model ="gpt-4o-mini",
            messages=messages,
            tools = tools # list of tools passed
        )

        finish_reason = response.choices[0].finish_reason

        # LLM can make a tool call here
        if finish_reason == "tool_calls":
            message = response.choices[0].message
            tool_calls = message.tool_calls

            #here the function is called
            results = handle_tool_calls(tool_calls)
            messages.append(message) # adds message as an element 
            messages.extend(results) # extend unpacks the list (results) into messages list

        else:
            done = True

    return response.choices[0].message.content





# Gradio chat interface
demo = gr.ChatInterface(
    fn=chat,
    title = "Chat with Mayank Malhotra",
    description= "ask about Mayanks professional career",
)

# launch
if __name__ == "__main__":
    demo.launch()


