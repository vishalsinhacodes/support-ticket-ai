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

## Setup
