from fastapi import FastAPI, HTTPException
from classifier import classify_ticket, analyze_ticket
from pydantic import BaseModel
import asyncio

app = FastAPI(
    title="Support Ticket AI",
    version="1.0.0",
)

@app.get("/")
def health_check():
    return {"status": "Ok"}


class UserRequest(BaseModel):
    ticket_text: str
    
class BatchRequest(BaseModel):
    tickets: list[str] 
    
class UserResponse(BaseModel):
    pass    
    
@app.post("/classify")
async def classify(request: UserRequest):
    try:
        result = await asyncio.to_thread(classify_ticket, request.ticket_text)
        return {"category": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="LLM not available")

@app.post("/analyze")
async def analyze(request: UserRequest):
    try:
        result = await asyncio.to_thread(analyze_ticket, request.ticket_text)
        return {"analysis": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))    
    except Exception:
        raise HTTPException(status_code=502, detail="LLM not available")
    
@app.post("/classify/batch")
async def classify_batch(request: BatchRequest):
    tasks = [asyncio.to_thread(classify_ticket, ticket) for ticket in request.tickets]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_count = len(results)
    success_count = 0
    failed_count = 0
    results_list = []
    
    
    for ticket, result in zip(request.tickets, results):
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
async def analyze_batch(request: BatchRequest):

    tasks = [asyncio.to_thread(analyze_ticket, ticket) for ticket in request.tickets]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_counts = len(results)
    success_count = 0
    failed_count = 0
    results_list = []
    
    for ticket, result in zip(request.tickets, results):
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
        
            