from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from database import create_document, db

app = FastAPI(title="Portfolio Backend", version="1.0.0")

# Allow all origins for simplicity in this ephemeral dev environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=5000)
    source: Optional[str] = Field(None, description="Optional source/page identifier")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/test")
async def test_db():
    """Quick DB connectivity check."""
    if db is None:
        return {"database": "unavailable"}
    collections = await _list_collections_safe()
    return {"database": "ok", "collections": collections}


async def _list_collections_safe():
    try:
        return db.list_collection_names()
    except Exception:
        return []


@app.post("/contact")
async def submit_contact(payload: ContactMessage):
    try:
        doc_id = create_document("contact", payload)
        return {"ok": True, "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
