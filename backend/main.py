from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from typing import List, Dict
import os

from backend.config import UPLOAD_DIR
from backend.document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mind Mate AI Chatbot", description="Travel Assistant with RAG")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Mind Mate AI Chatbot - Your Travel Assistant"}

@app.post("/upload-document/")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for processing"""
    try:
        # Check if filename is provided
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Save uploaded file
        file_path = os.path.join(str(UPLOAD_DIR), file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process document
        processor = DocumentProcessor()
        documents = processor.process_document(file_path)
        
        return {
            "filename": file.filename,
            "status": "success",
            "chunks_created": len(documents)
        }
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)