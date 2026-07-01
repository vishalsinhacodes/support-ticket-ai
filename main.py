import os
from fastapi.security import APIKeyHeader
from fastapi import Security
from fastapi import FastAPI, HTTPException, Depends, Request
from classifier import classify_ticket, analyze_ticket
from pydantic import BaseModel
from multi_agent import process_tickets_batch
import asyncio
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

API_KEY = os.environ.get("APP_API_KEY", "dev-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

app = FastAPI(
    title="Support Ticket AI",
    version="1.0.0",
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type:ignore

@app.get("/")
def health_check():
    return {"status": "Ok"}


class UserRequest(BaseModel):
    ticket_text: str
    
class BatchRequest(BaseModel):
    tickets: list[str] 
    
class UserResponse(BaseModel):
    pass    

async def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return key
    
@app.post("/classify")
@limiter.limit("5/minute")
async def classify(request: Request, body: UserRequest, key: str = Depends(verify_api_key)):
    try:
        result = await asyncio.to_thread(classify_ticket, body.ticket_text)
        return {"category": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="LLM not available")

@app.post("/analyze")
@limiter.limit("5/minute")
async def analyze(request: Request, body: UserRequest, key: str = Depends(verify_api_key)):    
    try:
        result = await asyncio.to_thread(analyze_ticket, body.ticket_text)
        return {"analysis": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))    
    except Exception:
        raise HTTPException(status_code=502, detail="LLM not available")
    
@app.post("/classify/batch")
@limiter.limit("3/minute")
async def classify_batch(request: Request, body: BatchRequest, key: str = Depends(verify_api_key)):
    tasks = [asyncio.to_thread(classify_ticket, ticket) for ticket in body.tickets]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_count = len(results)
    success_count = 0
    failed_count = 0
    results_list = []
    
    
    for ticket, result in zip(body.tickets, results):
        if isinstance(result, Exception):
            failed_count += 1
        else:
            success_count += 1
            
        status = "failed" if isinstance(result, Exception) else "success"
        category = str(result) if isinstance(result, Exception) else result
                
        results_list.append(
            {
                "ticket_text": ticket,
                "category": category,
                "status": status
            }
        )
    
    return {
        "results": results_list,
        "total": total_count,
        "successful": success_count,
        "failed": failed_count
    }
    
@app.post("/analyze/batch")
@limiter.limit("3/minute")
async def analyze_batch(request: Request, body: BatchRequest, key: str = Depends(verify_api_key)):

    tasks = [asyncio.to_thread(analyze_ticket, ticket) for ticket in body.tickets]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_counts = len(results)
    success_count = 0
    failed_count = 0
    results_list = []
    
    for ticket, result in zip(body.tickets, results):
        if isinstance(result, Exception): 
            failed_count += 1
        else:
            success_count += 1
            
        status = "failed" if isinstance(result, Exception) else "success"
        analysis = str(result) if isinstance(result, Exception) else result
        
        results_list.append(
            {
                "ticket_text": ticket,
                "analysis": analysis,
                "status": status
            }
        )
        
    return {
        "result": results_list,
        "total": total_counts,
        "success": success_count,
        "failed": failed_count
    }
    
@app.post("/process/batch")
@limiter.limit("3/minute")
async def process_batch(request: Request, body: BatchRequest, key: str = Depends(verify_api_key)):
    result = await process_tickets_batch(body.tickets)
    return result
    
        
        
            