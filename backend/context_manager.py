from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class Message:
    """Represents a single message in the conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class RetrievedDocument:
    """Represents a retrieved document"""
    id: str
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

class ContextManager:
    """Manages conversation context and retrieved documents for the RAG system"""
    
    def __init__(self, max_context_length: int = 4096):
        """
        Initialize the context manager
        
        Args:
            max_context_length (int): Maximum context length in tokens
        """
        self.max_context_length = max_context_length
        self.conversation_history: List[Message] = []
        self.retrieved_documents: List[RetrievedDocument] = []
        self.current_query: Optional[str] = None
        
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a user message to the conversation history
        
        Args:
            content (str): Message content
            metadata (Optional[Dict[str, Any]]): Additional metadata
        """
        message = Message(
            role="user",
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        self.conversation_history.append(message)
        logger.debug(f"Added user message: {content[:50]}...")
        
    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an assistant message to the conversation history
        
        Args:
            content (str): Message content
            metadata (Optional[Dict[str, Any]]): Additional metadata
        """
        message = Message(
            role="assistant",
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        self.conversation_history.append(message)
        logger.debug(f"Added assistant message: {content[:50]}...")
        
    def set_current_query(self, query: str) -> None:
        """
        Set the current query being processed
        
        Args:
            query (str): Current query
        """
        self.current_query = query
        logger.debug(f"Set current query: {query}")
        
    def add_retrieved_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add retrieved documents to the context
        
        Args:
            documents (List[Dict[str, Any]]): List of retrieved documents
        """
        for doc in documents:
            retrieved_doc = RetrievedDocument(
                id=doc.get('id', ''),
                content=doc.get('content', ''),
                score=doc.get('score', 0.0),
                metadata=doc.get('metadata', {})
            )
            self.retrieved_documents.append(retrieved_doc)
            
        logger.debug(f"Added {len(documents)} retrieved documents")
        
    def get_context_window(self) -> Dict[str, Any]:
        """
        Get the current context window for the LLM
        
        Returns:
            Dict[str, Any]: Context window with conversation history and retrieved documents
        """
        # Trim conversation history if needed
        trimmed_history = self._trim_conversation_history()
        
        # Get most relevant documents (top 3)
        relevant_docs = sorted(self.retrieved_documents, key=lambda x: x.score, reverse=True)[:3]
        
        context = {
            "conversation_history": [asdict(msg) for msg in trimmed_history],
            "retrieved_documents": [asdict(doc) for doc in relevant_docs],
            "current_query": self.current_query
        }
        
        logger.debug(f"Generated context window with {len(trimmed_history)} history items and {len(relevant_docs)} documents")
        return context
        
    def _trim_conversation_history(self) -> List[Message]:
        """
        Trim conversation history to fit within context window
        
        Returns:
            List[Message]: Trimmed conversation history
        """
        # For simplicity, we'll just limit to the last 10 messages
        # In a real implementation, you would estimate token count
        max_history = 10
        if len(self.conversation_history) <= max_history:
            return self.conversation_history
        else:
            return self.conversation_history[-max_history:]
        
    def clear_context(self) -> None:
        """
        Clear the conversation context
        """
        self.conversation_history.clear()
        self.retrieved_documents.clear()
        self.current_query = None
        logger.debug("Cleared conversation context")
        
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current context
        
        Returns:
            Dict[str, Any]: Context summary
        """
        return {
            "conversation_length": len(self.conversation_history),
            "retrieved_documents_count": len(self.retrieved_documents),
            "current_query": self.current_query,
            "total_tokens_estimated": self._estimate_tokens()
        }
        
    def _estimate_tokens(self) -> int:
        """
        Estimate the total number of tokens in the context
        
        Returns:
            int: Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters
        total_chars = 0
        
        # Add conversation history
        for msg in self.conversation_history:
            total_chars += len(msg.content)
            
        # Add retrieved documents
        for doc in self.retrieved_documents:
            total_chars += len(doc.content)
            
        # Add current query
        if self.current_query:
            total_chars += len(self.current_query)
            
        return total_chars // 4