'''
========================
In this exercise I have created a UI with an AI backend to discuss about my professional experience.
=======================
'''

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
from pathlib import Path

load_dotenv(override=True)
openai = OpenAI()

BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)

pdf_path = BASE_DIR / "cv.pdf"
summary_path = BASE_DIR / "summary.txt"

# use pypdf to read the CV
reader = PdfReader(pdf_path)
linkedin = ""
for page in reader.pages:
    text= page.extract_text()
    if text:
        linkedin+=text

#print the parsed text
print(linkedin)

# read the summary text file
with open(summary_path, "r", encoding="utf-8") as f:
    summary=f.read()

#print the summary
print(summary)


name = "Mayank Malhotra"

system_prompt = f"You act as {name}. Your are answering questions on behalf of {name}'s website, \
    particulary questions related to  {name}'s career, background, skills and experience. \
    Your responsibility is to represent {name} for interactions on the website. \
    You are given summary of {name} and his LinkedIn CV which you will use to answer the questions. \
    Be professional, engaging, as if talking to a potential client or future employer. \
    If you do not know the anwer , say so."


system_prompt+= f"\n ##Summary: {summary}"
system_prompt+=f"\n ##LinkedIn: {linkedin}"

# print and and check the system prompt
print(system_prompt)


# design the chat function
def chat(message, history):
    #messages = [{"role": "system", "content": system_prompt}]
    #messages.extend(history)
    #messages.append({"role": "user", "content":message})

    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]

    response=openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content

# adding the gradio chat interface
demo = gr.ChatInterface(
    fn=chat,
    title = "Chat with Mayank Malhotra",
    description= "ask about Mayanks professional career",
)

# launch
if __name__ == "__main__":
    demo.launch()