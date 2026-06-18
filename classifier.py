from openai import OpenAI
import json
import logging
from logging.handlers import RotatingFileHandler
import time
import functools


# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create rotating file handler
handler = RotatingFileHandler(
    filename="app.log",
    maxBytes=5 * 1024 * 1024,   # 5MB per file
    backupCount=3               # keep last 3 files
)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)

def time_taken(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"OpenAI call took {duration:.2f}s")
        return result
    return wrapper

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

@time_taken
def classify_ticket(ticket_text: str):
    logger.info(f"ticket_text: {ticket_text}")
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
        
        raw = response.choices[0].message.content
        logger.info(f"Raw Response: {raw}")
        return raw
    except Exception as e:
        logger.error(f"LLM service Unavailable: {e}")
        raise Exception(f"LLM Service unavailable: {e}")

@time_taken    
def analyze_ticket(ticket_text: str):
    logger.info(f"ticket_text: {ticket_text}")
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
        logger.info(f"Raw Response: {raw}")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raw = raw.strip()
            raw = raw.removeprefix("```json ").removesuffix("```").strip()
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                logger.error("Failed to parse response")
                return {
                    "error": "Failed to parse response",
                    "raw": raw
                }
            
    except Exception as e:
        logger.error(f"LLM service Unavailable: {e}")
        raise Exception(f"LLM Service Unavailable: {e}")
        