from classifier import analyze_ticket, classify_ticket, client, MODEL
import json
from typing import Any
from logger import get_logger

logger = get_logger(__name__)

def count_words(ticket_text: str) -> int:
    return len(ticket_text.split(" "))

def get_priority(ticket_text: str) -> str:
    analyze_data = analyze_ticket(ticket_text)
    
    return analyze_data.get("priority") or ""

tools: list[Any] = [
    {
        "type": "function",
        "function": {
            "name": "classify_ticket",
            "description": "Returns category after analysis of the ticket_text",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_text": {
                        "type": "string",
                        "description": "Ticket text is send by user"
                    }
                },
                "required": ["ticket_text"],
                "additionalProperties": False
            }
        }
    },    
    {
        "type": "function",
        "function": {
            "name": "count_words",
            "description": "Returns count of the words in the ticket text",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_text": {
                        "type": "string",
                        "description": "Ticket text is send by user"
                    }
                },
                "required": ["ticket_text"],
                "additionalProperties": False
            }
        }
    },    
    {
        "type": "function",
        "function": {
            "name": "get_priority",
            "description": "Returns priority after analysis of the ticket_text",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_text": {
                        "type": "string",
                        "description": "Ticket text is send by user"
                    }
                },
                "required": ["ticket_text"],
                "additionalProperties": False
            }
        }
    }        
]
    
SYSTEM_PROMPT = """
You are support ticket analysis assistant.
You have access to three tools. You need to think step by step before calling any tool.
You need to call tools as needed and use their results to form a final answer.
Answer should be in JSON format and No markdown anywhere in the final answer.
"""

def run_agent(question: str):
    messages: Any = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": question
        }
    ]
    
    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
        logger.info(f"Raw message from the LLM: {msg}")
        
        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name                     # type:ignore
                args = json.loads(tc.function.arguments)    # type:ignore
                
                logger.info(f"Function name: {name}, Function arguments: {args}")
                
                # Call the right function
                if name == "classify_ticket":
                    result = classify_ticket(args["ticket_text"])
                    logger.info(f"classify_ticket result : {result}")
                elif name == "count_words":
                    result = count_words(args["ticket_text"])
                    logger.info(f"count_words result : {result}")
                elif name == "get_priority":
                    result = get_priority(args["ticket_text"])
                    logger.info(f"get_priority result : {result}")
                else:
                    result = "Unknown tool"
                    logger.error("Unknown tool")
                
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": str(result)
                    }
                )
        else:
            logger.info(f"Final result : {msg.content}")
            return msg.content
   
if __name__ == "__main__":
    # print(run_agent("What is the category and word count of this ticket: My payment failed and I was charged twice")) 
    print(run_agent("What is the priority and category of this ticket, and how many words does it have: URGENT our entire system is down we are losing money every minute"))      