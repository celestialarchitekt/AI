'''
================================================
   LLM as a JUDGE - Evaluator, with Gradio as UI
================================================
'''


# region Imports
import os
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from pypdf import PdfReader
from pathlib import Path
# endregion


# region Load secret variables and create OpenAI instance
load_dotenv(override=True)
openai = OpenAI()
# endregion


# region Path for CV and Summary
BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)

pdf_path = BASE_DIR / "cv.pdf"
summary_path = BASE_DIR / "summary.txt"
# endregion


# region Define Pydantic Schema once
class Evaluation(BaseModel):
    feedback: str
    is_acceptable: bool
# endregion


# region Pypdf to read the CV
reader = PdfReader(pdf_path)
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text
# endregion


# region Summary text file
with open(summary_path, "r", encoding="utf-8") as f:
    summary = f.read()
#endregion


# region LLM Judge Prompt
name = "JudgeLLM"
evaluator_system_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
    You are given a conversation between user and an agent, your task is to decide whether the agents latest response is of acceptable quality. \
    The agent is playing the role of {name} and is representing {name} on their website. \
    The agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
    The agent has been provided with a context on {name} in the form of their summary and linkedin details. Here is the information: "

evaluator_system_prompt += f"\n ##Summary: {summary}"
evaluator_system_prompt += f"\n ##LinkedIn: {linkedin}"  
evaluator_system_prompt += "\n With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."
# endregion


#  region System Prompt
system_prompt = f"You act as {name}. Your are answering questions on behalf of {name}'s website, \
    particulary questions related to {name}'s career, background, skills and experience. \
    Your responsibility is to represent {name} for interactions on the website. \
    You are given summary of {name} and his LinkedIn CV which you will use to answer the questions. \
    Be professional, engaging, as if talking to a potential client or future employer. \
    If you do not know the answer, say so."

system_prompt += f"\n ##Summary: {summary}"
system_prompt += f"\n ##LinkedIn: {linkedin}"
# endregion


# region Evaluator User Prompt Function
def evaluator_user_prompt(reply, message, history):
    user_prompt = f"here is the conversation between the user and the agent: {history}"
    user_prompt += f"\n here is the last message from the user: {message}"
    user_prompt += f"\n here is the latest message from the agent: {reply}"
    user_prompt += "\n Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt
# endregion


# region Evaluate Function 
def evaluate(reply, message, history) -> Evaluation:
    messages = [
        {"role": "system", "content": evaluator_system_prompt},
        {"role": "user", "content": evaluator_user_prompt(reply, message, history)}
    ]
    response = openai.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=Evaluation
    )
  
    return response.choices[0].message.parsed
# endregion


# region System LLM Call
user_query = "do you hold a patent?"
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_query}
]

response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages
)

answer = response.choices[0].message.content
print(f"Agent Answer:\n{answer}\n")
#endregion


# region Gradio to integrate LLM as judge
def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content":message}]

    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages
    )

    reply = response.choices[0].message.content

    eval_result = evaluate(reply, message, history)
    

    print(" ---- \n\n priting evaluation results ----")
    print(eval_result.is_acceptable)
    print(eval_result.feedback)
    
    return reply

# endregion

# region adding the gradio chat interface
demo = gr.ChatInterface(
    fn=chat,
    title = "Chat with Mayank Malhotra",
    description= "ask about Mayanks professional career",
)
# endregion

# region launch
if __name__ == "__main__":
    demo.launch()

#endregion