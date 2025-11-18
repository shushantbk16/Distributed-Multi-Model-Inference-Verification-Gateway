# main.py additions (Redis Client Setup)
from gateway_free import run_free_ensemble
from dotenv import load_dotenv
load_dotenv()  # <--- THIS IS MISSING. IT LOADS THE .ENV FILE.

# ... then your other imports ...
from fastapi import FastAPI
from upstash_redis.asyncio import Redis as AsyncRedis


from upstash_redis.asyncio import Redis as AsyncRedis
from fastapi import Depends, HTTPException
from functools import lru_cache
import json

# Initialize the client based on environment variables
@lru_cache()
def get_upstash_client() -> AsyncRedis:
    # Use Redis.from_env() to load from UPSTASH_REDIS_REST_URL and TOKEN
    return AsyncRedis.from_env()

# Dependency to inject Redis client into routes
async def get_redis_client() -> AsyncRedis:
    return get_upstash_client()



# main.py - The API Definition
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# Assume call_llama3, call_gemini_flash, etc. are defined above or imported

# --- Pydantic Schemas (Non-negotiable input/output validation) ---
# Resume Insight: Demonstrates understanding of type checking and API standards.

class QueryInput(BaseModel):
    """Defines the required input format for the API."""
    query: str = Field(..., description="The user's input query or question.")

class ModelResult(BaseModel):
    """Defines the structure for each model's result."""
    model: str
    status: str
    duration: float
    content: str | None = None
    error: str | None = None

class EnsembleResponse(BaseModel):
    """Defines the final API response structure."""
    input_query: str
    final_judge_result: str  # We will fill this with the best answer later
    model_results: List[ModelResult]

app = FastAPI(
    title="LLM Ensemble Gateway",
    description="A non-blocking, multi-model inference system.",
    version="1.0.0"
)

CACHE_TTL = 3600  # 1 hour

@app.post("/ensemble", response_model=EnsembleResponse)
async def ensemble_inference(
    input_data: QueryInput, 
    redis_client: AsyncRedis = Depends(get_redis_client) # Inject the Redis client
):
    query = input_data.query
    
    # --- STEP 1: CACHE CHECK (Latency Optimization) ---
    # Resume Insight: Demonstrates Cache-Aside Pattern
    cached_data = await redis_client.get(query)
    if cached_data:
        # If cached, return instantly (This is the 50ms win)
        print(f"CACHE HIT for: {query}")
        return EnsembleResponse(**json.loads(cached_data))

    # --- STEP 2: EXECUTE ENGINE (The Concurrent Call) ---
    # Assume run_free_ensemble is defined and returns structured ModelResult list
    
    # Run the existing concurrent LLM calls
    model_results = await run_free_ensemble(query) # This calls Llama/Gemini simultaneously

    # --- STEP 3: THE JUDGE (Aggregation Logic - Simple Version) ---
    # We will replace this with a smart prompt later. For now, pick the fastest.
    
    successful_results = [r for r in model_results if r['status'] == 'success']
    if not successful_results:
        raise HTTPException(status_code=500, detail="All LLM Providers Failed")
        
    # Judge Logic: Pick the result with the lowest duration (fastest)
    best_result = min(successful_results, key=lambda x: x['duration'])
    final_best_answer = (
        f"[JUDGE: Chose {best_result['model']} in {best_result['duration']:.2f}s] "
        f"{best_result['content']}"
    )

    # --- STEP 4: CACHE SET (Cost/Performance) ---
    final_response = EnsembleResponse(
        input_query=query,
        final_judge_result=final_best_answer,
        model_results=model_results
    )
    
    # Store the final structured response in Redis as a JSON string
    await redis_client.set(query, final_response.model_dump_json(), ex=CACHE_TTL)
    
    return final_response

if __name__ == "__main__":
    # We use Uvicorn for production, but in Codespaces you'll run it differently.
    # We will skip this block and use the terminal command (Step 3).
    pass