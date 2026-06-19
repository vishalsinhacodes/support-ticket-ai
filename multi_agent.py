from classifier import client, MODEL, time_taken, logger, analyze_ticket
import asyncio

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

# if __name__ == "__main__":
#     result = process_ticket("URGENT: system is down, losing money every minute")
#     print(result)
    
async def process_tickets_batch(tickets: list[str]):
    tasks = [asyncio.to_thread(process_ticket, ticket) for ticket in tickets]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_counts = len(results)
    success_count = 0
    failed_count = 0
    results_list = []
    
    for result, ticket in zip(results, tickets):
        if isinstance(result, Exception):
            failed_count += 1
        else:
            success_count += 1
            
        status = "failed" if isinstance(result, Exception) else "success"
        response = str(result) if isinstance(result, Exception) else result
        
        results_list.append(
            {
                "ticket_text": ticket,
                "response": response,
                "status": status
            }
        )
        
    return {
        "result": results_list,
        "total": total_counts,
        "success": success_count,
        "failed": failed_count
    }  
    
if __name__ == "__main__":
    tickets = [
        "My payment failed and I was charged twice",
        "URGENT: system is down, losing money every minute",
        "What are your business hours?"
    ]
    result = asyncio.run(process_tickets_batch(tickets))
    print(result)    
      