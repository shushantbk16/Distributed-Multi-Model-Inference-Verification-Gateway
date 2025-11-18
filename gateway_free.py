import asyncio
import os
import time
from dotenv import load_dotenv
from groq import AsyncGroq
import google.generativeai as genai

# Load env vars
load_dotenv()


groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))



async def call_llama3(query):
    """Calls Llama-3-70b via Groq (Free & Fast)."""
    try:
        start = time.time()
        chat_completion = await groq_client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
        )
        duration = time.time() - start
        return {
            "model": "Llama-3 (Groq)",
            "status": "success",
            "duration": duration,
            "content": chat_completion.choices[0].message.content
        }
    except Exception as e:
        return {"model": "Llama-3", "status": "error", "error": str(e)}

async def call_gemini_flash(query):
    """Calls Gemini 1.5 Flash (Free & Smart)."""
    try:
        start = time.time()
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = await asyncio.to_thread(model.generate_content, query)
        duration = time.time() - start
        return {
            "model": "Gemini Flash",
            "status": "success",
            "duration": duration,
            "content": response.text
        }
    except Exception as e:
        return {"model": "Gemini Flash", "status": "error", "error": str(e)}

# --- THE ORCHESTRATOR ---

async def run_free_ensemble(query):
    print(f"🚀 Processing Query on FREE Stack: '{query}'")
    
    # Fire requests in parallel
    results = await asyncio.gather(
        call_llama3(query),
        call_gemini_flash(query)
        
    )
    
    print("\n--- RESULTS ---")
    for res in results:
        if res["status"] == "success":
            print(f"✅ {res['model']} finished in {res['duration']:.4f}s")
        else:
            print(f"❌ {res['model']} Failed: {res['error']}")
            
    return results

if __name__ == "__main__":
    asyncio.run(run_free_ensemble("Write a Python script to sort a list using QuickSort."))