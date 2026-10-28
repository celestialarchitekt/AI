"""
==========================================
LangChain - Streaming using stream_events()
==========================================
"""

from langchain.agents import create_agent
from dotenv import load_dotenv


load_dotenv(override=True)

agent = create_agent(
    model = "gpt-4o-mini",
   
)

# Run Program
if __name__  == "__main__":
    
    stream = agent.stream_events(
    {"messages": [{"role":"user", "content": "tell me munich weather"}]},
     version = "v3"
        
    )
    
      
    for chunk in stream:
        if isinstance(chunk, dict):
            params = chunk['params'] #params is a dict
            data = params['data'] #data is tuple
            
            if isinstance(data,tuple) and len(data)>0:
                pass
                #print("data is a tuple")
                #print(data)
                
            elif isinstance(data, dict) and len(data)>0:
                #print("data is a dict")
                data_dict = data
                content_dict= data_dict['messages'][-1].content[0]
                
                if isinstance(content_dict, dict):
                    #print(f"content_dict is of type: {type(content_dict)}")
                    response = content_dict.get('text')
                    
                    print("--------- FINAL RESPONSE ----------")
                    print(response)
        else:
            print("not a dictionary")