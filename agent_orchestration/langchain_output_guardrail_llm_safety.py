from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime
from langchain.messages import AIMessage
from langchain.chat_models import init_chat_model
from typing import Any
from dotenv import load_dotenv

# load ENV VARs
load_dotenv(override=True)

# define class for output check
class SafetyGuardrailMiddleware(AgentMiddleware):
    """Model-based guardrail: Use an LLM to evaluate response safety."""

    def __init__(self):
        #super().__init__()
        self.safety_model = init_chat_model("gpt-5.4-mini")

    @hook_config(can_jump_to=["end"])
    
    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # Get the final AI response
        # AgentState is a typeddict uses a class syntax
        
        #print(type(state)) # is a dictionary
        #print(type(AgentState)) # is a typed_dictionary
        
        if not state["messages"]:
            return None

        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return None

        # Use a model to evaluate safety
        safety_prompt = f"""Evaluate if this response is safe and appropriate.
        Respond with only 'SAFE' or 'UNSAFE'.

        Response: {last_message.content}"""

        # invoke an LLM model to check the output
        result = self.safety_model.invoke([{"role": "user", "content": safety_prompt}])

        if "UNSAFE" in result.content:
            last_message.content = "I cannot provide that response. Please rephrase your request."

        return None


# Use the safety guardrail
from langchain.agents import create_agent


agent = create_agent(
    model="gpt-4o-mini",
    middleware=[SafetyGuardrailMiddleware()],
)



# Run the main function
if __name__ == "__main__":
    result = agent.invoke({
        "messages": [{"role": "user", "content": "How do I make explosives?"}]
    })
    
    print("------------ FINAL RESULT------------")
    print(result["messages"][-1].content)
    
    
    
# -----------------------------------------------------------------------
    
"""
During execution: agent.invoke() runs step-by-step. Whenever the main LLM generates a response, the framework packages the current conversation history into the state dictionary and passes it directly to your after_agent hook.

Inside after_agent: state["messages"] gives you access to the full message history up to that exact moment. state["messages"][-1] targets the AI's latest response.

When UNSAFE is detected: You modify last_message.content directly. Because Python passes objects by reference, updating last_message.content changes the actual text held inside that message object in memory.

The Return: The hook then finishes (return None).

After execution: Once all steps and hooks finish, agent.invoke() finally completes and returns that updated state dictionary back to your if __name__ == "__main__": block.

At Runtime (Execution): state behaves 100% like a standard Python dictionary. You access and mutate its data using square brackets (e.g., state["messages"]).

At Development Time (IDE/Type Checking): Your code editor treats AgentState like a structured class, providing autocompletion and warning you if you try to access a key that doesn't exist (like state["invalid_key"]).
    
"""
    
    