from classifier import client, MODEL, time_taken, logger, analyze_ticket

RESPONSE_AGENT_PROMPT = """
You are a helpful response agent.
You will get ticket_text, category and priority on the basis of these you have write 
polite, professional replies to customer.
No markdown in the response.
"""

# Agent 1 - Reponse Agent
@time_taken
def write_response(ticket_text: str, category: str, priority: str) -> str:
    logger.info(f"Writing response for: {ticket_text[:50]}")
    user_message = f"""
    Ticket: {ticket_text}
    Category: {category}
    Priority: {priority}
    
    Write a customer reply.
    """
    
    response = client.chat.completions.create(
        model = MODEL,
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": RESPONSE_AGENT_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )
    
    return response.choices[0].message.content or ""

# Agent 2 Manager Agent
def process_ticket(ticket_text: str):
    analyze_res = analyze_ticket(ticket_text)
    category = analyze_res.get("category", "general")
    priority = analyze_res.get("priority", "medium")
    sentiment = analyze_res.get("sentiment", "neutral")
    write_res = write_response(ticket_text, category, priority)
    
    return {
        "ticket_text": ticket_text,
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "customer_reply": write_res
    }

if __name__ == "__main__":
    result = process_ticket("URGENT: system is down, losing money every minute")
    print(result)