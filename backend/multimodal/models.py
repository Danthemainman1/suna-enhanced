"""
Pydantic models for multimodal capabilities.

This module defines all data models for vision, document parsing,
and audio processing.
"""

from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime


# Vision Models
class ImageDescription(BaseModel):
    """Description of an image."""
    
    description: str = Field(..., description="Overall description of the image")
    objects: list[str] = Field(default_factory=list, description="Detected objects")
    text: Optional[str] = Field(None, description="Extracted text (OCR)")
    colors: list[str] = Field(default_factory=list, description="Dominant colors")
    tags: list[str] = Field(default_factory=list, description="Image tags/labels")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ScreenAnalysis(BaseModel):
    """Analysis of a screenshot."""
    
    description: str = Field(..., description="What the screenshot shows")
    ui_elements: list[dict] = Field(default_factory=list, description="Detected UI elements")
    text_content: str = Field("", description="All visible text")
    interactions: list[str] = Field(default_factory=list, description="Possible interactions")
    page_type: Optional[str] = Field(None, description="Type of page/screen")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Document Parsing Models
class Table(BaseModel):
    """A table extracted from a document."""
    
    table_id: str = Field(..., description="Unique table identifier")
    headers: list[str] = Field(default_factory=list, description="Table headers")
    rows: list[list[str]] = Field(default_factory=list, description="Table rows")
    caption: Optional[str] = Field(None, description="Table caption")
    page_number: Optional[int] = Field(None, description="Page where table appears")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ParsedDocument(BaseModel):
    """Parsed document with extracted content."""
    
    filename: str = Field(..., description="Original filename")
    document_type: str = Field(..., description="Type of document (pdf, docx, etc)")
    title: Optional[str] = Field(None, description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    created_date: Optional[datetime] = Field(None, description="Creation date")
    text_content: str = Field("", description="Extracted text content")
    num_pages: int = Field(0, description="Number of pages")
    tables: list[Table] = Field(default_factory=list, description="Extracted tables")
    images: list[dict] = Field(default_factory=list, description="Image metadata")
    links: list[str] = Field(default_factory=list, description="Extracted links")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Audio Processing Models
class Transcription(BaseModel):
    """Transcription of audio content."""
    
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Transcription confidence")
    duration_seconds: float = Field(0.0, description="Audio duration")
    segments: list[dict] = Field(default_factory=list, description="Timestamped segments")
    words: list[dict] = Field(default_factory=list, description="Individual words with timestamps")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AudioSummary(BaseModel):
    """Summary of audio content."""
    
    summary: str = Field(..., description="Audio content summary")
    key_points: list[str] = Field(default_factory=list, description="Key points")
    speakers: Optional[int] = Field(None, description="Number of speakers detected")
    duration_seconds: float = Field(0.0, description="Audio duration")
    language: str = Field(..., description="Primary language")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
