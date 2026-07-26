from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from datetime import datetime
import uuid, os

from Backend.database.connect import db, documents_collection, chunks_collection
from Backend.utils.utils import extract_text_from_pdf, chunk_text
from Backend.utils.embedding import embed_text


# Create router with prefix
router = APIRouter(prefix="/admin", tags=["admin"])

# Collections
users_collection = db["users"]

# --- USER MANAGEMENT ---
@router.get("/users")
def list_users():
    data = list(users_collection.find({}, {"_id": 0, "password": 0}))
    return {"users": data}

@router.post("/users/add")
async def add_user(name: str = Form(...), email: str = Form(...), role: str = Form("user")):
    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User already exists")
    users_collection.insert_one({
        "name": name,
        "email": email,
        "role": role,
        "created_at": datetime.utcnow()
    })
    return {"message": "User added successfully"}

@router.delete("/users/remove")
async def remove_user(email: str = Form(...)):
    result = users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User removed successfully"}

# --- DOCUMENT MANAGEMENT ---
@router.get("/documents")
def list_documents():
    data = list(documents_collection.find({}, {"_id": 0}))
    return {"documents": data}

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    uploaded_by: str = Form("admin"),
    lang: str = Form("eng")
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_id = str(uuid.uuid4())
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    text = extract_text_from_pdf(save_path, lang=lang)
    if not text:
        raise HTTPException(status_code=400, detail="No text extracted from PDF")

    doc = {
        "file_id": file_id,
        "filename": file.filename,
        "uploaded_by": uploaded_by,
        "uploaded_at": datetime.utcnow(),
        "size_bytes": len(content),
        "storage_path": save_path,
        "language": lang
    }
    documents_collection.insert_one(doc)

    # Chunk and embed
    text_chunks = chunk_text(text)
    for idx, chunk in enumerate(text_chunks):
        embedding = embed_text(chunk)
        chunks_collection.insert_one({
            "doc_id": file_id,
            "chunk_id": f"{file_id}-{idx}",
            "text": chunk,
            "embedding": embedding,
            "metadata": {
                "source": file.filename,
                "index": idx,
                "uploaded_by": uploaded_by,
                "uploaded_at": datetime.utcnow(),
                "language": lang
            }
        })

    return {"message": "Document uploaded and processed", "file_id": file_id, "chunks": len(text_chunks)}

@router.delete("/documents/remove")
async def remove_document(file_id: str = Form(...)):
    doc = documents_collection.find_one({"file_id": file_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    chunks_collection.delete_many({"doc_id": file_id})
    documents_collection.delete_one({"file_id": file_id})
    try:
        os.remove(doc["storage_path"])
    except Exception:
        pass

    return {"message": "Document removed successfully"}