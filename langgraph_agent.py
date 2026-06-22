from typing import TypedDict, Optional
from classifier import analyze_ticket
from multi_agent import write_response
from langgraph.graph import StateGraph, END

class TicketState(TypedDict):
    ticket_text: str
    category: Optional[str]
    priority: Optional[str]
    sentiment: Optional[str]
    customer_reply: Optional[str]
    
    
def analyze_node(state: TicketState) -> dict:
    ticket_text = state["ticket_text"]
    analyze_res = analyze_ticket(ticket_text)
    
    return {
        "category": analyze_res["category"],
        "priority": analyze_res["priority"],
        "sentiment": analyze_res["sentiment"]
    }
    
def write_response_node(state: TicketState) -> dict:
    response = write_response(
        state["ticket_text"],
        str(state["category"]),
        str(state["priority"])
    )
    
    return {
        "customer_reply": response
    }
    
def build_graph():
    graph = StateGraph(TicketState)
    
    graph.add_node("analyze", analyze_node)
    graph.add_node("respond", write_response_node)
    
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "respond")
    graph.add_edge("respond", END)
    
    return graph.compile()

if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"ticket_text": "URGENT: system is down, losing money every minute"})   # type:ignore 
    print(result)