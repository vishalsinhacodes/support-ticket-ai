from openai import OpenAI
import json

client = OpenAI()
MODEL = "gpt-4o-mini"

CLASSIFY_SYSTEM_PROMPT = """
You are a helpful Assistant.
You need to read the ticket text and provide the response from below four categories:
    billing,
    technical,
    general,
    urgent
Return only a single word. No markdown, No explaination.
"""

ANALYZE_SYSTEM_PROMPT = """
You are a helpful assistant.
You need to read the ticket and after analysise need to return the response in below format
with attributes category, priority, summary, sentiment:
{
  "category": "billing",
  "priority": "high",
  "summary": "Customer charged despite failed payment",
  "sentiment": "frustrated"
}
Category should be billing, technical, general
Priority should be low, medium, high and critical.
Sentiment should be positive, neutral, frustrated, angry.
Response should be in JSON format and No markdown.
"""

def classify_ticket(ticket_text: str):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": CLASSIFY_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": ticket_text
                }
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"LLM Service unavailable: {e}")
    
def analyze_ticket(ticket_text: str):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": ANALYZE_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": ticket_text
                }
            ]
        )
        
        raw = response.choices[0].message.content or ""
        
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raw = raw.strip()
            raw = raw.removeprefix("```json ").removesuffix("```").strip()
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {
                    "error": "Failed to parse response",
                    "raw": raw
                }
            
    except Exception as e:
        raise Exception(f"LLM Service Unavailable: {e}")    
        