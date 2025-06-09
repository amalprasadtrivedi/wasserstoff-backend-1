from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
import os
import uuid
import json

from app.core.ocr import extract_text
from app.services.embedding_service import get_embedding, search_documents, init_faiss, add_to_index
from app.services.llm_service import generate_answer, summarize_themes
from app.services.llm_service import generate_answer, summarize_themes


# Store extracted texts in-memory (or replace with database)
DOCUMENTS_DB = []

router = APIRouter()
FAISS_INDEX = init_faiss()


@router.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        os.makedirs("app/data", exist_ok=True)  # Ensure folder exists

        file_path = f"app/data/{file_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        text = extract_text(file_path)
        if not text.strip():
            raise ValueError("OCR/Text extraction failed — no text detected.")

        doc_meta = {
            "id": file_id,
            "name": file.filename,
            "text": text
        }

        DOCUMENTS_DB.append(doc_meta)
        add_to_index(doc_meta["id"], text, FAISS_INDEX)

        return {
            "message": "File uploaded and processed successfully.",
            "doc_id": file_id,
            "preview": text[:300]
        }

    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"[UPLOAD ERROR] {error_detail}")
        return JSONResponse(
            status_code=500,
            content={"message": f"Internal server error during upload: {str(e)}"}
        )


@router.get("/documents/")
async def list_documents():
    return [{"id": doc["id"], "name": doc["name"]} for doc in DOCUMENTS_DB]


@router.post("/ask/")
async def ask_question(question: str = Form(...)):
    if not DOCUMENTS_DB:
        return JSONResponse(status_code=400, content={"message": "No documents uploaded yet."})

    # Search similar docs
    top_docs = search_documents(question, FAISS_INDEX, DOCUMENTS_DB)

    # Use LLM (Groq/LLAMA) to answer from each doc
    responses = []
    for doc in top_docs:
        answer = generate_answer(question, doc["text"])
        responses.append({
            "doc_id": doc["id"],
            "doc_name": doc["name"],
            "answer": answer,
            "citation": f"Doc: {doc['name'][:30]}..."
        })

    # Generate theme synthesis
    theme_summary = summarize_themes(question, [r["answer"] for r in responses])

    return {
        "question": question,
        "individual_answers": responses,
        "theme_summary": theme_summary
    }
