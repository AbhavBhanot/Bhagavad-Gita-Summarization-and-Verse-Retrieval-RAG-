"""
FastAPI backend for Bhagwad Gita RAG Chatbot
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from pathlib import Path

from backend.services.rag_service import RAGService
from backend.models.schemas import (
    QueryRequest, QueryResponse, HealthResponse,
    TranslationRequest, TranslationResponse, SupportedLanguagesResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="Bhagwad Gita RAG Chatbot API",
    description="API for querying Bhagwad Gita and Patanjali Yoga Sutras using RAG (Retrieval Augmented Generation)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
# Get CORS origins from environment variable or use defaults
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,https://spiritual-rag-chatbot.netlify.app").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service
rag_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG service on startup"""
    global rag_service
    try:
        # Use environment variable for data directory or default to relative path
        data_dir = os.getenv("DATA_DIR", str(Path(__file__).parent.parent / "dataset"))
        data_dir = Path(data_dir)
        
        print(f"Initializing RAG Service with data directory: {data_dir}")
        
        if not data_dir.exists():
            print(f"Warning: Data directory {data_dir} does not exist")
            # Try alternative paths for production
            alt_paths = [
                Path("/app/dataset"),
                Path("/opt/render/project/src/dataset"),
                Path("./dataset")
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    data_dir = alt_path
                    print(f"Using alternative data directory: {data_dir}")
                    break
        
        rag_service = RAGService(data_dir)
        await rag_service.initialize()
        print("RAG Service initialized successfully")
    except Exception as e:
        print(f"Error initializing RAG service: {e}")
        # Don't raise in production, just log the error
        if os.getenv("ENVIRONMENT") != "production":
            raise

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bhagwad Gita RAG Chatbot</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
            h1 { text-align: center; margin-bottom: 30px; }
            .api-info { background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; margin: 20px 0; }
            a { color: #FFD700; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🕉️ Bhagwad Gita RAG Chatbot API</h1>
            <div class="api-info">
                <h3>Welcome to the Spiritual Wisdom API</h3>
                <p>This API provides access to verses and wisdom from the Bhagavad Gita and Patanjali Yoga Sutras using advanced RAG (Retrieval Augmented Generation) technology.</p>
                
                <h4>📚 Features:</h4>
                <ul>
                    <li>Query-based verse retrieval from sacred texts</li>
                    <li>Intelligent matching using TF-IDF and cosine similarity</li>
                    <li>Automatic summary generation</li>
                    <li>Bilingual support (Sanskrit and English)</li>
                </ul>
                
                <h4>🔗 Quick Links:</h4>
                <ul>
                    <li><a href="/docs">📖 Interactive API Documentation (Swagger)</a></li>
                    <li><a href="/redoc">📋 Alternative API Documentation (ReDoc)</a></li>
                    <li><a href="/health">💚 Health Check</a></li>
                    <li><a href="/frontend">🌐 Frontend Application</a></li>
                </ul>
                
                <h4>🚀 Quick Test:</h4>
                <p>Try a sample query: <code>POST /query</code> with body: <code>{"query": "How to control the mind?"}</code></p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Bhagwad Gita RAG Chatbot API is running",
        version="1.0.0"
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a spiritual query and return relevant verses with summary
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    try:
        # Validate query
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Process the query
        result = await rag_service.process_query(
            query=request.query,
            top_n=request.top_n,
            include_summary=request.include_summary
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/sources")
async def get_available_sources():
    """Get information about available text sources"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    return await rag_service.get_sources_info()

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text to supported languages"""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    try:
        translated_text = await rag_service.translate_text(request.text, request.target_language)
        
        if translated_text.startswith("Language") or translated_text.startswith("Translation failed"):
            raise HTTPException(status_code=400, detail=translated_text)
        
        language_name = rag_service.supported_languages.get(request.target_language, "Unknown")
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            target_language=request.target_language,
            language_name=language_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.get("/supported-languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """Get list of supported languages for translation"""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    return SupportedLanguagesResponse(languages=rag_service.supported_languages)

# Mount static files for frontend
static_path = Path(__file__).parent.parent / "frontend" / "build"
if static_path.exists():
    app.mount("/frontend", StaticFiles(directory=static_path, html=True), name="frontend")

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"Starting Bhagwad Gita RAG Chatbot API on {host}:{port}")
    print(f"CORS Origins: {cors_origins}")
    
    uvicorn.run(
        "main:app", 
        host=host, 
        port=port, 
        reload=os.getenv("ENVIRONMENT") != "production",
        log_level=os.getenv("LOG_LEVEL", "info")
    )

