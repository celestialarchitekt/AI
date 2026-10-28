"""
=============================
LangChain - Input Guardrails
============================
"""

from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime
from langchain.agents import create_agent
from dotenv import load_dotenv


# load the ENV VARs
load_dotenv(override=True)


class ContentFilterMiddleware(AgentMiddleware):
    """ block requests having banned keywords """
    
    def __init__(self, banned_keywords: list[str]):
        #super().__init__()
        
        ll=[]
        for kw in banned_keywords:
            ll.append(kw.lower())
            
        # assign ll out of the loop!
        self.banned_keywords = ll 
        
        #using list comprehension
        #self.banned_keywords = [kw.lower() for kw in banned_keywords]
    
    
    
    @hook_config(can_jump_to=["end"])
    def before_agent(self, state: AgentState, runtime:Runtime)->dict[str, any] | None:
         
         #empty , no messages
         if not state["messages"]:
             return None
         
         # get the first message
         first_message = state["messages"][0]
         
         #check type
         if first_message.type!= "human":
             return None
         
         # get content
         content = first_message.content.lower()
         
         for keyword in self.banned_keywords:
            if keyword in content:
                 
                 return {
                     "messages" : [{
                         "role": "assistant",
                         "content": "I cannot process the request"
                     }],
                     
                     "jump_to" : "end"
                 }

    
         return None



agent = create_agent(
        model = "gpt-4o-mini",
        middleware = [
            ContentFilterMiddleware(
                banned_keywords = ["hack", "exploit", "malware"]
            ) 
        ]
    )
    
    
if __name__ == "__main__":
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "how do i play hack a database"}]}
        )
        
        
        print(result["messages"][-1].content)
        
        
# ======================================================================================================== #       
