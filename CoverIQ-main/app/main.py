# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import models, db, retrieval

app = FastAPI(title="CoverIQ API - Permanent Knowledge Base")

# --- CORS middleware ---
origins = ["http://localhost", "http://localhost:8080", "null"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables if they don't exist
# This is useful for the ingestion script to track processed files
models.Base.metadata.create_all(bind=db.engine)

# --- Simplified Pydantic Model ---
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    context: str

# --- REMOVED /upload/ ENDPOINT ---

@app.post("/query/", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    Endpoint to ask a question about the permanent knowledge base.
    """
    if not request.query or request.query.isspace():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    try:
        # No doc_id is needed anymore
        answer, context = retrieval.retrieve_and_generate(query=request.query)
        return QueryResponse(answer=answer, context=context)
    except Exception as e:
        print(f"Error during query: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred during the query.")
