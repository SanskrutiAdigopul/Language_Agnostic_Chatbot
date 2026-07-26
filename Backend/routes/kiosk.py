from fastapi import APIRouter
from Backend.database.connect import documents_collection, chunks_collection
from groq import Groq
import os

kiosk_router = APIRouter(prefix="/api/kiosk", tags=["Kiosk"])

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)


@kiosk_router.get("/latest")
async def get_latest_circular():
    """
    Returns the latest document's summary for the ESP32 OLED display.
    Summary is kept short (~200 chars) for the 128x64 OLED screen.
    """
    # Get the most recently uploaded document
    doc = documents_collection.find_one(sort=[("_id", -1)])

    if not doc:
        return {"status": "no_docs", "title": "No Circulars", "summary": "No documents uploaded yet."}

    # Get the first chunk of the document for a preview
    first_chunk = chunks_collection.find_one({"doc_id": doc.get("file_id")})

    if first_chunk:
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": f"Summarize this college circular in under 150 characters. "
                               f"Be concise and informative:\n\n{first_chunk['text'][:500]}"
                }],
                max_tokens=100
            )
            summary = response.choices[0].message.content.strip()
        except Exception:
            summary = first_chunk["text"][:150] + "..."
    else:
        summary = "Circular uploaded but no text extracted."

    return {
        "status": "ok",
        "title": doc.get("filename", "Untitled")[:50],
        "summary": summary[:200]
    }


@kiosk_router.get("/status")
async def kiosk_status():
    """
    Simple health check endpoint for ESP32 to verify connectivity.
    """
    doc_count = documents_collection.count_documents({})
    return {"ok": True, "docs": doc_count}
