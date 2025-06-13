from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from main import fact_check_bot  # Import the fact_check_bot function directly

import os
import logging

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Current working directory: {os.getcwd()}")

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html on root
@app.get("/")
async def read_index():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"error": "index.html not found in /static"})


# Fact-check API endpoint
@app.post("/fact-check")
async def fact_check(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "").strip()

        if not query:
            return JSONResponse(status_code=400, content={"error": "Query cannot be empty"})

        result = fact_check_bot(query)

        if isinstance(result, dict) and "response" in result:
            return {"response": result["response"]}
        else:
            return JSONResponse(status_code=500, content={"error": "Unexpected response structure"})

    except Exception as e:
        logger.error(f"Error in /fact-check endpoint: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.get("/fact-check")
async def debug_fact_check_get():
    logging.warning("⚠️ Someone is trying to GET /fact-check — Not allowed.")
    return JSONResponse(status_code=405, content={"error": "Use POST request"})

# Optional health check
# @app.get("/health")
# def health_check():
#     return {"status": "OK"}
