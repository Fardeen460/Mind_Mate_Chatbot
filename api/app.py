from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from typing import List, Dict, Any
import os
import uuid
from datetime import datetime

# Local imports
from backend.config import UPLOAD_DIR
from backend.document_processor import DocumentProcessor
from backend.embeddings import EmbeddingModel
from backend.vector_store import VectorStore
from backend.retriever import HybridRetriever
from backend.context_manager import ContextManager
from backend.metrics import MetricsTracker, PerformanceMetrics

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

# Initialize components
document_processor = DocumentProcessor()
embedding_model = EmbeddingModel()
vector_store = VectorStore()
retriever = HybridRetriever(vector_store, embedding_model)
context_manager = ContextManager()
metrics_tracker = MetricsTracker()

@app.get("/api")
async def root():
    return {"message": "Welcome to Mind Mate AI Chatbot - Your Travel Assistant"}

@app.post("/api/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Start timer for metrics
        metrics_tracker.start_timer("document_processing")
        
        # Check if filename is provided
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Save uploaded file
        file_path = os.path.join(str(UPLOAD_DIR), file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process document
        documents = document_processor.process_document(file_path)
        
        # Add to retriever
        doc_entries = [{"content": doc.page_content, "metadata": doc.metadata} for doc in documents]
        doc_ids = retriever.add_documents(doc_entries)
        
        # Stop timer and record metrics
        processing_time = metrics_tracker.stop_timer("document_processing")
        
        logger.info(f"Processed document {file.filename} with {len(documents)} chunks")
        
        return {
            "filename": file.filename,
            "status": "success",
            "chunks_created": len(documents),
            "processing_time": f"{processing_time:.2f}s"
        }
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/api/chat")
async def chat(query: Dict[str, str]):
    """Process a chat query using RAG"""
    logger.info(f"Received chat query: {query}")
    try:
        user_query = query.get("message", "")
        logger.info(f"Extracted message: {user_query}")
        if not user_query:
            logger.error("No message provided in query")
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Start timers for metrics
        metrics_tracker.start_timer("total_response")
        metrics_tracker.start_timer("query_processing")
        
        # Set current query in context
        context_manager.set_current_query(user_query)
        context_manager.add_user_message(user_query)
        
        # Stop query processing timer
        query_processing_time = metrics_tracker.stop_timer("query_processing")
        metrics_tracker.start_timer("document_retrieval")
        
        # Retrieve relevant documents
        try:
            retrieved_docs = retriever.retrieve(user_query)
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            # Fallback to built-in guidance when retriever fails
            response = _fallback_response(user_query)
            total_time = metrics_tracker.stop_timer("total_response")
            # Record minimal metrics
            performance_metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                query_processing_time=0.0,
                document_retrieval_time=0.0,
                response_generation_time=0.0,
                total_response_time=total_time,
                documents_retrieved=0,
                documents_used=0,
                context_length=len(user_query),
                query_length=len(user_query),
                response_length=len(response),
                similarity_scores=[]
            )
            metrics_tracker.record_metrics(performance_metrics)
            return {
                "query": user_query,
                "response": response,
                "confidence": 80.0,
                "documents_retrieved": 0,
                "response_time": f"{total_time:.2f}s",
                "retrieved_documents": []
            }
        
        # Stop document retrieval timer
        retrieval_time = metrics_tracker.stop_timer("document_retrieval")

        # If no documents were retrieved, use fallback guidance
        if not retrieved_docs:
            logger.info("No documents retrieved, using fallback guidance")
            response = _fallback_response(user_query)
            total_time = metrics_tracker.stop_timer("total_response")
            performance_metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                query_processing_time=0.0,
                document_retrieval_time=retrieval_time,
                response_generation_time=0.0,
                total_response_time=total_time,
                documents_retrieved=0,
                documents_used=0,
                context_length=len(user_query),
                query_length=len(user_query),
                response_length=len(response),
                similarity_scores=[]
            )
            metrics_tracker.record_metrics(performance_metrics)
            return {
                "query": user_query,
                "response": response,
                "confidence": 75.0,
                "documents_retrieved": 0,
                "response_time": f"{total_time:.2f}s",
                "retrieved_documents": []
            }
        metrics_tracker.start_timer("response_generation")
        
        # Add retrieved documents to context
        context_manager.add_retrieved_documents(retrieved_docs)
        
        # Generate response (simulated)
        # In a real implementation, you would use an LLM here
        response = _generate_response(user_query, retrieved_docs)
        
        # Stop response generation timer
        generation_time = metrics_tracker.stop_timer("response_generation")
        total_time = metrics_tracker.stop_timer("total_response")
        
        # Add assistant message to context
        context_manager.add_assistant_message(response)
        
        # Record metrics
        similarity_scores = [doc['score'] for doc in retrieved_docs]
        performance_metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            query_processing_time=query_processing_time,
            document_retrieval_time=retrieval_time,
            response_generation_time=generation_time,
            total_response_time=total_time,
            documents_retrieved=len(retrieved_docs),
            documents_used=min(3, len(retrieved_docs)),  # Using top 3
            context_length=len(user_query) + sum(len(doc['content']) for doc in retrieved_docs),
            query_length=len(user_query),
            response_length=len(response),
            similarity_scores=similarity_scores
        )
        metrics_tracker.record_metrics(performance_metrics)
        
        # Prepare response with metadata
        response_data = {
            "query": user_query,
            "response": response,
            "confidence": _calculate_confidence(retrieved_docs),
            "documents_retrieved": len(retrieved_docs),
            "response_time": f"{total_time:.2f}s",
            "retrieved_documents": [
                {
                    "id": doc['id'],
                    "content": doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'],
                    "score": doc['score'],
                    "metadata": doc['metadata']
                }
                for doc in retrieved_docs[:3]  # Top 3 documents
            ]
        }
        
        logger.info(f"Processed query: {user_query}")
        
        return response_data
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat query: {str(e)}")

@app.get("/api/metrics")
async def get_metrics():
    """Get performance metrics"""
    try:
        metrics_summary = metrics_tracker.get_metrics_summary()
        return metrics_summary
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")

@app.get("/api/documents")
async def get_documents():
    """Get list of processed documents"""
    try:
        doc_count = vector_store.get_document_count()
        return {
            "document_count": doc_count,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error retrieving document info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving document info: {str(e)}")

def _generate_response(query: str, documents: List[Dict[str, Any]]) -> str:
    """
    Generate a response based on the query and retrieved documents
    In a real implementation, this would use an LLM
    """
    # Simple rule-based response generation for demo
    if not documents:
        return "I don't have specific information about that topic in my knowledge base. Could you provide more details or ask about something else related to travel?"
    
    # Get the highest scoring document
    best_doc = max(documents, key=lambda x: x['score'])
    
    # Simple response based on document content
    if "beach" in query.lower() or "ocean" in query.lower():
        return "Based on my travel knowledge, beaches are wonderful destinations for relaxation. " + \
               best_doc['content'][:200] + "..." if len(best_doc['content']) > 200 else best_doc['content']
    elif "hotel" in query.lower() or "accommodation" in query.lower():
        return "For accommodations, I recommend considering location and amenities. " + \
               best_doc['content'][:200] + "..." if len(best_doc['content']) > 200 else best_doc['content']
    elif "food" in query.lower() or "restaurant" in query.lower():
        return "Food is an essential part of travel experience. " + \
               best_doc['content'][:200] + "..." if len(best_doc['content']) > 200 else best_doc['content']
    else:
        # Generic response
        return "Based on my travel knowledge: " + \
               best_doc['content'][:300] + "..." if len(best_doc['content']) > 300 else best_doc['content']

def _calculate_confidence(documents: List[Dict[str, Any]]) -> float:
    """
    Calculate confidence score based on retrieved documents
    """
    if not documents:
        return 0.0
    
    # Use the highest similarity score as confidence (scaled to 0-100)
    best_score = max(doc['score'] for doc in documents)
    confidence = min(100.0, best_score * 100)
    return round(confidence, 2)

def _fallback_response(query: str) -> str:
    """
    Provide a safe, helpful fallback response when retrieval or indexing fails.
    This is a rule-based helper for common travel queries to improve UX.
    """
    q = query.lower()
    # Destination-specific quick tips
    if 'jammu' in q:
        return (
            "Jammu (in Jammu & Kashmir) is a great base for religious visits and mountain access. "
            "Quick tips: 1) Visit Vaishno Devi (allow 1-2 days). 2) Pack warm clothes if you go to higher altitudes. "
            "3) Local transport: taxis and hired cabs; confirm fares in advance. 4) Try local food like rajma and kaladi. "
            "If you want, upload any local guides or itineraries (PDF/DOCX) and I'll use them to give detailed day-by-day plans."
        )
    if 'hotel' in q or 'accommodation' in q:
        return (
            "For finding hotels: pick a neighbourhood close to the attractions you want, check recent reviews, "
            "and filter by your budget and required amenities (Wi‑Fi, breakfast, free cancellation)."
        )
    if 'flight' in q or 'airline' in q:
        return (
            "For flights: search flexible dates 2–3 months ahead, consider mid‑week departures, and use price alerts. "
            "If you give me your departure city and dates, I can suggest a strategy."
        )

    # Generic helpful fallback
    return (
        "I don't have matching documents in my knowledge base right now. "
        "You can upload travel documents (itineraries, guides, bookings) using the 'Upload Travel Documents' button — "
        "after that I'll provide specific, document-backed recommendations. Meanwhile, tell me the destination and travel dates and I'll give general planning tips."
    )