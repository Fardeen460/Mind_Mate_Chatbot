from typing import List, Dict, Any, Optional, Tuple, Union
import logging
from backend.embeddings import EmbeddingModel
from backend.vector_store import VectorStore, QueryResult
from backend.config import EMBEDDING_MODEL, TOP_K_RESULTS

logger = logging.getLogger(__name__)

class HybridRetriever:
    """Hybrid retrieval system combining vector search and keyword matching"""
    
    def __init__(self, vector_store: Optional[VectorStore] = None, embedding_model: Optional[EmbeddingModel] = None):
        """
        Initialize the hybrid retriever
        
        Args:
            vector_store (VectorStore): Vector store instance
            embedding_model (EmbeddingModel): Embedding model instance
        """
        self.vector_store = vector_store or VectorStore()
        self.embedding_model = embedding_model or EmbeddingModel(EMBEDDING_MODEL)
        
    def retrieve(self, query: str, top_k: int = TOP_K_RESULTS, metadata_filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents using hybrid approach
        
        Args:
            query (str): Query text
            top_k (int): Number of results to return
            metadata_filter (Optional[Dict]): Metadata filter for search
            
        Returns:
            List[Dict[str, Any]]: Retrieved documents with relevance scores
        """
        try:
            # Perform vector search
            vector_results = self._vector_search(query, top_k, metadata_filter)
            
            # Combine and rank results
            combined_results = self._combine_results(vector_results, top_k)
            
            logger.info(f"Retrieved {len(combined_results)} documents for query: {query}")
            return combined_results
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
    
    def _vector_search(self, query: str, top_k: int, metadata_filter: Optional[Dict] = None) -> QueryResult:
        """
        Perform vector similarity search
        
        Args:
            query (str): Query text
            top_k (int): Number of results to return
            metadata_filter (Optional[Dict]): Metadata filter for search
            
        Returns:
            QueryResult: Vector search results
        """
        try:
            # Search vector store
            results = self.vector_store.search(query, top_k, metadata_filter)
            
            logger.debug(f"Vector search returned {len(results['ids'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            raise
    
    def _combine_results(self, vector_results: QueryResult, top_k: int) -> List[Dict[str, Any]]:
        """
        Combine and rank results from different retrieval methods
        
        Args:
            vector_results (QueryResult): Results from vector search
            top_k (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: Combined and ranked results
        """
        try:
            combined = []
            
            # Check if we have results
            if (vector_results['ids'] and 
                len(vector_results['ids']) > 0 and 
                len(vector_results['ids'][0]) > 0):
                
                # Process vector search results
                ids = vector_results['ids'][0]
                documents = vector_results['documents'][0] if vector_results['documents'] else []
                metadatas = vector_results['metadatas'][0] if vector_results['metadatas'] else []
                distances = vector_results['distances'][0] if vector_results['distances'] else []
                
                for i, doc_id in enumerate(ids[:top_k]):
                    # Safely get document content
                    content = documents[i] if i < len(documents) else ""
                    
                    # Safely get metadata
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    
                    # Safely calculate score
                    score = 1.0
                    if i < len(distances):
                        score = 1 - distances[i]
                    
                    result = {
                        'id': doc_id,
                        'content': content,
                        'metadata': metadata,
                        'score': score,
                        'source': 'vector'
                    }
                    combined.append(result)
            
            # Sort by score (highest first)
            combined.sort(key=lambda x: x['score'], reverse=True)
            
            logger.debug(f"Combined results: {len(combined)} documents")
            return combined[:top_k]
        except Exception as e:
            logger.error(f"Error combining results: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add documents to the retriever system
        
        Args:
            documents (List[Dict[str, Any]]): List of documents with 'content' and 'metadata'
            
        Returns:
            List[str]: List of document IDs
        """
        try:
            # Add to vector store
            doc_ids = self.vector_store.add_documents(documents)
            
            logger.info(f"Added {len(documents)} documents to retriever system")
            return doc_ids
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise