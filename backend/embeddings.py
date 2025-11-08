from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union, Sequence
import logging

logger = logging.getLogger(__name__)

class EmbeddingModel:
    """Handles text embeddings using Sentence Transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model
        
        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading embedding model {model_name}: {str(e)}")
            raise
    
    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Encode text(s) into embeddings
        
        Args:
            texts (Union[str, List[str]]): Single text or list of texts to encode
            
        Returns:
            Union[List[float], List[List[float]]]: Embedding vector(s)
        """
        try:
            if isinstance(texts, str):
                # Single text
                embedding = self.model.encode(texts).tolist()
                logger.debug(f"Encoded single text into embedding of size {len(embedding)}")
                return embedding
            else:
                # List of texts
                embeddings = self.model.encode(texts).tolist()
                logger.debug(f"Encoded {len(texts)} texts into embeddings of size {len(embeddings[0])}")
                return embeddings
        except Exception as e:
            logger.error(f"Error encoding text(s): {str(e)}")
            raise
    
    def get_similarity(self, embedding1: Sequence[float], embedding2: Sequence[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1 (List[float]): First embedding
            embedding2 (List[float]): Second embedding
            
        Returns:
            float: Cosine similarity score
        """
        try:
            # Convert to numpy arrays
            emb1 = np.array(embedding1)
            emb2 = np.array(embedding2)
            
            # Calculate cosine similarity
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            raise