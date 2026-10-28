"""
============================
LangChain - Runtime Context
============================
"""

from dotenv import load_dotenv
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest


#Load api keys
load_dotenv(override=True)

@dataclass
class Context:
    user_role : str
    deployment_env : str
    
    
    
@dynamic_prompt
def context_aware_prompt(request:ModelRequest)->str:
    
    print("---triggered middleware ---")
    
    context:Context = request.runtime.context
    user_role = request.runtime.context.user_role
    env = request.runtime.context.deployment_env

    base = " you are a helpful assistant"
    
    if user_role=="admin":
        base+= "\n you have admin access, you can perform all operations"
        
    elif user_role == "viewer":
        base+= "\n you have read only access, guide users to read operations"
        
    if env=="production":
        base+="\n be extra careful with any data modification"
        
    print(base)
    return base




#create the agent
agent = create_agent(
    model = "gpt-5.4-mini",
    middleware=[context_aware_prompt],
    
)



# run the code
if __name__ == "__main__":
    
    runtime_ctx = Context(user_role="viewer", deployment_env="production")
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What is capital of Germany?"}]},
        context = runtime_ctx
    )
    
    print("--- result ------")
    print(result["messages"][-1].content)