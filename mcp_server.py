from mcp.server.fastmcp import FastMCP
from classifier import classify_ticket, analyze_ticket
import json

mcp = FastMCP("Support Ticket AI")

@mcp.tool()
def classify(ticket_text: str) -> str:
    """Classify a support ticket into billing, technical, general, or urgent category.
    """
    
    return classify_ticket(ticket_text) or ""

@mcp.tool()
def analyze(ticket_text: str) -> str:
    """
    Analyze a support ticket into attributes category, priority, summary, sentiment.
    """
    
    res = analyze_ticket(ticket_text)
    return json.dumps(res)
    

if __name__ == "__main__":
    mcp.run()
    