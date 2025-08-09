"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class SourceType(str, Enum):
    """Enumeration for text sources"""
    GITA = "Gita"
    PYS = "PYS"

class QueryRequest(BaseModel):
    """Request model for spiritual query"""
    query: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="The spiritual question or topic to search for",
        example="How to control the mind?"
    )
    top_n: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of relevant verses to retrieve",
        example=5
    )
    include_summary: bool = Field(
        default=True,
        description="Whether to include AI-generated summary",
        example=True
    )
    source_filter: Optional[List[SourceType]] = Field(
        default=None,
        description="Filter results by text source (Gita, PYS, or both)",
        example=["Gita", "PYS"]
    )

class Verse(BaseModel):
    """Model representing a single verse/shloka"""
    chapter: Optional[float] = Field(
        None,
        description="Chapter number",
        example=2.0
    )
    verse: Optional[float] = Field(
        None,
        description="Verse number",
        example=47.0
    )
    text: str = Field(
        ...,
        description="Main text content",
        example="कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।"
    )
    sanskrit: Optional[str] = Field(
        None,
        description="Sanskrit verse text",
        example="कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।"
    )
    translation: Optional[str] = Field(
        None,
        description="English translation",
        example="You have a right to perform your prescribed duty, but not to the fruits of action."
    )
    source: SourceType = Field(
        ...,
        description="Source text (Gita or PYS)",
        example="Gita"
    )
    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity score with query",
        example=0.85
    )
    concept: Optional[str] = Field(
        None,
        description="Main concept or theme",
        example="Karma Yoga"
    )
    keyword: Optional[str] = Field(
        None,
        description="Key philosophical term",
        example="Detachment"
    )

class QueryResponse(BaseModel):
    """Response model for spiritual query"""
    query: str = Field(
        ...,
        description="Original query",
        example="How to control the mind?"
    )
    retrieved_verses: List[Verse] = Field(
        ...,
        description="List of relevant verses",
        min_items=0,
        max_items=20
    )
    summary: Optional[str] = Field(
        None,
        description="AI-generated summary of the verses",
        example="The retrieved verses emphasize the importance of controlling the mind through practice, detachment, and devotion to the divine."
    )
    total_results: int = Field(
        ...,
        description="Total number of verses found",
        example=5
    )
    processing_time_ms: float = Field(
        ...,
        description="Time taken to process the query in milliseconds",
        example=245.5
    )

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(
        ...,
        description="Service status",
        example="healthy"
    )
    message: str = Field(
        ...,
        description="Status message",
        example="Bhagwad Gita RAG Chatbot API is running"
    )
    version: str = Field(
        ...,
        description="API version",
        example="1.0.0"
    )

class SourceInfo(BaseModel):
    """Information about a text source"""
    name: str = Field(
        ...,
        description="Source name",
        example="Bhagavad Gita"
    )
    code: SourceType = Field(
        ...,
        description="Source code",
        example="Gita"
    )
    total_verses: int = Field(
        ...,
        description="Total number of verses",
        example=700
    )
    chapters: int = Field(
        ...,
        description="Number of chapters",
        example=18
    )
    description: str = Field(
        ...,
        description="Brief description",
        example="A 700-verse Hindu scripture that is part of the epic Mahabharata"
    )

class SourcesResponse(BaseModel):
    """Response model for available sources"""
    sources: List[SourceInfo] = Field(
        ...,
        description="List of available text sources"
    )
    total_verses: int = Field(
        ...,
        description="Total verses across all sources",
        example=895
    )

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(
        ...,
        description="Error type",
        example="ValidationError"
    )
    message: str = Field(
        ...,
        description="Error message",
        example="Query cannot be empty"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )

class TranslationRequest(BaseModel):
    """Request model for text translation"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Text to translate",
        example="The essence of yoga is to control the mind"
    )
    target_language: str = Field(
        ...,
        description="Target language code (hi, fr, de, es, it, pt, ru, ja, ko, zh)",
        example="hi"
    )

class TranslationResponse(BaseModel):
    """Response model for text translation"""
    original_text: str = Field(
        ...,
        description="Original text in English"
    )
    translated_text: str = Field(
        ...,
        description="Translated text"
    )
    target_language: str = Field(
        ...,
        description="Target language code"
    )
    language_name: str = Field(
        ...,
        description="Target language name"
    )

class SupportedLanguagesResponse(BaseModel):
    """Response model for supported languages"""
    languages: Dict[str, str] = Field(
        ...,
        description="Dictionary of language codes to language names"
    )

