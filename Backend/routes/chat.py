from fastapi import APIRouter, Form
from Backend.utils.embedding import embed_text
from Backend.utils.faiss_index import build_faiss_index
from Backend.database.connect import chunks_collection
import numpy as np
from groq import Groq
from langdetect import detect

router = APIRouter(prefix="/chat", tags=["chat"])

GROQ_API_KEY = "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" 

def call_gemini(prompt: str) -> str:
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )
    return response.choices[0].message.content

@router.post("/query")
async def chat_query(
    query: str = Form(...),
    top_k: int = Form(3),
    lang: str = Form(None)
):
    if not lang:
        try:
            lang = detect(query)
        except Exception:
            lang = "English"

    query_embedding = embed_text(query)
    index, ids = build_faiss_index()

    if index is None:
        return {"response": "No documents available for search."}

    D, I = index.search(np.array([query_embedding]).astype("float32"), top_k)
    matched_ids = [ids[i] for i in I[0]]
    results = list(
        chunks_collection.find({"chunk_id": {"$in": matched_ids}}, {"_id": 0})
    )

    context_chunks = "\n\n".join([r["text"] for r in results])
    prompt = f"""
You are a helpful multilingual campus assistant.
Answer the student's question using the provided context.
Reply in {lang}.

Context:
{context_chunks}

Question:
{query}

Answer:
"""

    try:
        reply = call_gemini(prompt)
    except Exception as e:
        reply = f"LLM error: {str(e)}"

    return {"response": reply}