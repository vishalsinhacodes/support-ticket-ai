# Support Ticket AI

Support Ticket AI is a system that automatically classifies and analyzes customer support
tickets using OpenAI's GPT-4o-mini.

For example, if a customer reports being charged twice for a payment, a support operator
would normally have to read the ticket, decide which team should handle it, and route it
manually. This project automates that decision - reading the ticket and returning the
category, priority, and sentiment automatically.

Build with FastAPI and OpenAI. It has two core capabilities: quick category classification,
and full structured analysis including priority and sentiment.

## Architecture

Request -> FastAPI -> OpenAI(gpt-4o-mini) -> Response

FastAPI: Receives request then validates input and routes requests to respective endpoint.
OpenAI: Reads the ticket and apply system prompt and few-shots example to give idea to LLM
how to respond aftet the analysis.
Response: Once LLM has responded the output will a category string if it a classify request
therwise a detailed JSON structure for analyze request.

## Endpoint

| Method | Endpoint        | Description                                                                                                                                          |
| ------ | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| POST   | /classify       | It takes one ticket_text and after processing returned category of the ticket                                                                        |
| POST   | /analyze        | It takes one ticket_text and after processing returned detailed JSON structured of the ticket                                                        |
| POST   | /classify/batch | It takes multiple ticket_texts and after processing returned category of the ticket along with total count, success and failed count                 |
| POST   | /analyze/batch  | It takes multiple ticket_texts and after processing returned detailed JSON structured of the ticket along with total count, success and failed count |
| POST   | /process/batch  | Takes multiple tickets, runs each through the multi-agent pipeline (analyze + respond), returns results with total/success/failed counts             |

## Setup

1. Clone the repo
   git clone https://github.com/vishalsinhacodes/support-ticket-ai.git
   cd support-ticket-ai

2. Create and activate virtual environment

   Windows:
   python -m venv venv
   venv\Scripts\activate

   Mac/Linux:
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt

4. Set your OpenAI API key as environment variable
   The application reads OPENAI_API_KEY automatically from your environment.
   Get your key from https://platform.openai.com/api-keys

   Windows:
   set OPENAI_API_KEY=your_key_here

   Mac/Linux:
   export OPENAI_API_KEY=your_key_here

   Alternatively, you can use a .env file:
   1. Install python-dotenv
      pip install python-dotenv
   2. Create a .env file in the project root
      OPENAI_API_KEY=your_key_here
   3. Add this to the top of main.py
      from dotenv import load_dotenv
      load_dotenv()

5. Run the server
   uvicorn main:app --reload

API docs available at http://localhost:8000/docs

## Example Usage

Single classification:
curl -X POST http://localhost:8000/classify \
 -H "Content-Type: application/json" \
 -d "{\"ticket_text\": \"My payment failed but I was charged twice\"}"

Response:
{"category": "billing"}

Full analysis:
curl -X POST http://localhost:8000/analyze \
 -H "Content-Type: application/json" \
 -d "{\"ticket_text\": \"URGENT: system is down, losing money every minute\"}"

Response:
{
"analysis": {
"category": "technical",
"priority": "critical",
"summary": "System outage causing financial loss",
"sentiment": "frustrated"
}
}

Batch classification:
curl -X POST http://localhost:8000/classify/batch \
 -H "Content-Type: application/json" \
 -d "{\"tickets\": [\"My payment failed\", \"App keeps crashing\", \"What are your hours?\"]}"

Response:
{
"results": [...],
"total": 3,
"successful": 3,
"failed": 0
}

## Agentic Patterns

### ReAct Agent

A standalone agent (react_agent.py) that follows the Reasoning + Acting pattern. It has
access to three tools — classify_ticket, count_words, and get_priority. Given a question,
the agent thinks about what information it needs, calls the appropriate tool, observes
the result, and either calls another tool or returns a final answer. Each step is logged
for full observability — the model's reasoning, tool calls, arguments, and results are
all visible in the log file.

### Multi-Agent Pipeline

A 2-agent system (multi_agent.py) with a clear separation of concerns. The Analyzer Agent
extracts category, priority, and sentiment from a ticket. The Response Agent takes those
results and writes a professional, customer-facing reply. A manager function coordinates
both agents sequentially — Agent 2 depends on Agent 1's output, so they cannot run
concurrently. The full pipeline also supports concurrent batch processing across multiple
tickets using asyncio.gather().

## Design Decisions

- **Schema separation — removed `urgent` from categories** — In the original schema,
  `urgent` appeared as both a category and overlapped with priority levels. If a billing
  issue was also urgent, the LLM had to choose between `category: billing` and
  `category: urgent` — it couldn't capture both. Removing `urgent` from categories and
  adding `critical` to priority means a ticket can now be `category: billing, 
priority: critical` simultaneously — two separate pieces of information, no ambiguity.

- **Async batch processing with asyncio.gather()** — Processing 100 tickets sequentially
  would take ~100 seconds (1 second per OpenAI call). Using asyncio.gather() with
  asyncio.to_thread() runs all tickets concurrently — each gets its own thread, all
  OpenAI calls happen simultaneously, total time drops to ~1 second regardless of batch size.

- **Independent failure handling in batch** — If one ticket fails, the rest still succeed.
  Each item is wrapped in try/except inside asyncio.gather(return_exceptions=True) so a
  single bad input never crashes the whole batch.

- **Single OpenAI client instance** — The client is created once at module level, not
  inside each function call. This avoids connection overhead on every request and is more
  efficient under load.

- **Centralized logging in logger.py** — Initially each module (classifier.py, react_agent.py)
  had its own logger with no handler attached, so logs from react_agent.py were going nowhere.
  Moving the RotatingFileHandler setup into a single logger.py module means any file can import
  get_logger() and immediately have working file-based logging — one place controls log format,
  rotation size, and file location for the entire project.
