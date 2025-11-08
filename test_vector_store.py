#!/usr/bin/env python3
"""
Test script for vector_store.py
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_vector_store():
    try:
        # Try to import the VectorStore class
        from backend.vector_store import VectorStore
        print("✓ VectorStore imported successfully")
        
        # Try to create an instance
        vector_store = VectorStore()
        print("✓ VectorStore instance created successfully")
        
        # Try to get document count
        count = vector_store.get_document_count()
        print(f"✓ Document count retrieved: {count}")
        
        print("All tests passed!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_vector_store()