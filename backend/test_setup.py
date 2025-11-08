import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from embeddings import EmbeddingModel
from vector_store import VectorStore
from document_processor import DocumentProcessor

def test_embeddings():
    """Test the embedding model"""
    print("Testing embeddings...")
    try:
        model = EmbeddingModel()
        embedding = model.encode("Hello, travel world!")
        print(f"Embedding generated successfully. Length: {len(embedding)}")
        return True
    except Exception as e:
        print(f"Error testing embeddings: {e}")
        return False

def test_vector_store():
    """Test the vector store"""
    print("Testing vector store...")
    try:
        store = VectorStore()
        print(f"Vector store initialized. Document count: {store.get_document_count()}")
        return True
    except Exception as e:
        print(f"Error testing vector store: {e}")
        return False

def test_document_processor():
    """Test the document processor"""
    print("Testing document processor...")
    try:
        processor = DocumentProcessor()
        print("Document processor initialized successfully")
        return True
    except Exception as e:
        print(f"Error testing document processor: {e}")
        return False

if __name__ == "__main__":
    print("Testing Mind Mate AI Chatbot components...")
    print("=" * 50)
    
    tests = [
        test_document_processor,
        test_embeddings,
        test_vector_store
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    print("=" * 50)
    if all(results):
        print("All tests passed! Your setup is working correctly.")
    else:
        print("Some tests failed. Please check the errors above.")