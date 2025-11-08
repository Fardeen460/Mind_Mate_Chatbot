import os
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredExcelLoader
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document loading and chunking for the RAG system"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a document based on its file extension
        
        Args:
            file_path (str): Path to the document file
            
        Returns:
            List[Document]: List of loaded documents
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == ".pdf":
                loader = PyPDFLoader(file_path)
            elif file_extension in [".docx", ".doc"]:
                loader = UnstructuredWordDocumentLoader(file_path)
            elif file_extension in [".xlsx", ".xls"]:
                loader = UnstructuredExcelLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks
        
        Args:
            documents (List[Document]): List of documents to chunk
            
        Returns:
            List[Document]: List of chunked documents
        """
        try:
            chunked_documents = self.text_splitter.split_documents(documents)
            logger.info(f"Split documents into {len(chunked_documents)} chunks")
            return chunked_documents
            
        except Exception as e:
            logger.error(f"Error chunking documents: {str(e)}")
            raise
    
    def process_document(self, file_path: str) -> List[Document]:
        """
        Load and chunk a document
        
        Args:
            file_path (str): Path to the document file
            
        Returns:
            List[Document]: List of processed (chunked) documents
        """
        documents = self.load_document(file_path)
        chunked_documents = self.chunk_documents(documents)
        return chunked_documents