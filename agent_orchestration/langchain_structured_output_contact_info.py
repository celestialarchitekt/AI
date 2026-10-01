
# Imports
from langchain.agents import create_agent
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load API Key
load_dotenv(override=True)



class ContactInfo(BaseModel):
    name:str = Field(description="name of person")
    email:str = Field(description="email address of person")
    phone:str = Field(description = "phone number of person")


# Create LangChain Agent
agent = create_agent(
    model = "gpt-4o-mini",
    response_format=ContactInfo
)


# Run Main
if __name__ == "__main__":
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"}]}
    )
    
    
    print(response["structured_response"])