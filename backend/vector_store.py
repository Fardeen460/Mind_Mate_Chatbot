import chromadb
from chromadb.config import Settings
from chromadb.api.types import QueryResult
from typing import List, Dict, Any, Optional
import uuid
import logging
from backend.config import CHROMA_DIR, CHROMA_COLLECTION

logger = logging.getLogger(__name__)

class VectorStore:
    """Handles vector storage and retrieval using ChromaDB"""
    
    def __init__(self, collection_name: str = CHROMA_COLLECTION):
        """
        Initialize ChromaDB client and collection
        
        Args:
            collection_name (str): Name of the collection to use
        """
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection_name = collection_name
            self.collection = self.client.get_or_create_collection(name=collection_name)
            
            logger.info(f"Initialized ChromaDB collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add documents to the vector store
        
        Args:
            documents (List[Dict[str, Any]]): List of documents with 'content', 'metadata' keys
            
        Returns:
            List[str]: List of document IDs
        """
        try:
            # Generate IDs for documents
            ids = [str(uuid.uuid4()) for _ in documents]
            
            # Extract contents and metadata
            contents = [doc['content'] for doc in documents]
            metadatas = [doc.get('metadata', {}) for doc in documents]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(documents)} documents to collection")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def search(self, query: str, n_results: int = 5, metadata_filter: Optional[Dict] = None) -> QueryResult:
        """
        Search for similar documents
        
        Args:
            query (str): Query text
            n_results (int): Number of results to return
            metadata_filter (Optional[Dict]): Metadata filter for search
            
        Returns:
            QueryResult: Search results
        """
        try:
            # Prepare search parameters
            search_params = {
                "query_texts": [query],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"]  # Include distances for similarity scoring
            }
            
            # Add metadata filter if provided
            if metadata_filter:
                search_params["where"] = metadata_filter
            
            # Perform search
            results = self.collection.query(**search_params)
            
            # Safely get the number of results for logging
            result_count = 0
            if results['ids'] and len(results['ids']) > 0:
                result_count = len(results['ids'][0])
            
            logger.debug(f"Search returned {result_count} results")
            return results
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise
    
    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by IDs
        
        Args:
            ids (List[str]): List of document IDs to delete
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from collection")
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise
    
    def get_document_count(self) -> int:
        """
        Get the total number of documents in the collection
        
        Returns:
            int: Number of documents
        """
        try:
            count = self.collection.count()
            logger.debug(f"Collection contains {count} documents")
            return count
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            raise

    def clear_collection(self) -> None:
        """
        Clear all documents from the collection
        """
        try:
            # Get all document IDs
            all_ids = self.collection.get(include=[])["ids"]
            if all_ids:
                self.collection.delete(ids=all_ids)
            logger.info("Cleared all documents from collection")
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            raise
