# Mind Mate AI Chatbot

An intelligent travel assistant powered by Retrieval-Augmented Generation (RAG) technology.

## Overview

Mind Mate AI Chatbot is a sophisticated travel assistant that combines the power of large language models with retrieval-augmented generation to provide accurate, context-aware travel recommendations and information. The system uses vector embeddings, ChromaDB for vector storage, and a hybrid retrieval system to deliver personalized travel assistance.

## Features

### Backend Features
- **Document Processing & Chunking**: Processes various document formats (PDF, DOCX, XLSX) and intelligently chunks content
- **Vector Embeddings**: Uses Sentence Transformers for generating high-quality embeddings
- **ChromaDB Integration**: Efficient vector storage and similarity search
- **Hybrid Retrieval System**: Combines vector search with potential for keyword matching
- **Context Window Management**: Manages conversation history and retrieved documents
- **Performance Metrics Tracking**: Monitors and logs system performance

### Frontend Features
- **Enhanced Chat Interface**: Modern, responsive chat UI
- **Real-time Retrieval Visualization**: Shows what documents were used to generate responses
- **Confidence Scoring**: Displays confidence levels for each response
- **Source Attribution**: Shows which documents informed each response
- **Metadata Display**: Provides additional context about retrieved information

## Architecture

The system follows a modular architecture with the following key components:

1. **Document Processor**: Handles document loading and intelligent chunking
2. **Embedding Model**: Generates vector representations of text
3. **Vector Store**: Manages vector storage and similarity search using ChromaDB
4. **Hybrid Retriever**: Combines multiple retrieval strategies
5. **Context Manager**: Maintains conversation context and retrieved documents
6. **Metrics Tracker**: Monitors system performance
7. **Frontend**: Interactive web interface for user interaction

## Key RAG Components

- **Dual Encoder Architecture**: Separates encoding of queries and documents
- **Document Chunking Strategies**: Optimized chunking for travel content
- **Vector Similarity Search**: Efficient retrieval using cosine similarity
- **Context-Aware Response Generation**: Considers conversation history
- **Performance Monitoring**: Real-time metrics and monitoring

## Getting Started

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Mind_Mate_AI_Chatbot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python backend/app.py
   ```

4. Access the application at `http://localhost:8000`

### API Endpoints

- `POST /upload-document/` - Upload and process travel documents
- `POST /chat/` - Interact with the AI assistant
- `GET /metrics/` - Retrieve performance metrics
- `GET /documents/` - Get information about processed documents

## Usage

1. Upload travel documents (guides, itineraries, etc.) using the document upload feature
2. Ask travel-related questions in the chat interface
3. View confidence scores and source documents for each response
4. Monitor system performance through the metrics dashboard

## Project Structure

```
Mind_Mate_AI_Chatbot/
├── backend/
│   ├── __init__.py
│   ├── app.py              # Main application
│   ├── config.py           # Configuration settings
│   ├── document_processor.py # Document loading and chunking
│   ├── embeddings.py       # Embedding model interface
│   ├── vector_store.py     # ChromaDB integration
│   ├── retriever.py        # Hybrid retrieval system
│   ├── context_manager.py  # Conversation context management
│   └── metrics.py          # Performance tracking
├── frontend/
│   ├── index.html          # Main interface
│   ├── styles.css          # Styling
│   └── script.js           # Client-side logic
├── data/                   # Processed documents
├── chroma_db/              # Vector database
├── uploads/                # Uploaded files
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Sentence Transformers for embedding generation
- ChromaDB for vector storage
- FastAPI for the web framework