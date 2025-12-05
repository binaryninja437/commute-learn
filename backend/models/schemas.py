"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ProcessingStage(str, Enum):
    """Processing pipeline stages"""
    UPLOAD = "upload"
    OCR = "ocr"
    SCRIPT = "script"
    TTS = "tts"
    DONE = "done"
    ERROR = "error"


class ProcessingStatus(BaseModel):
    """Status of a processing job"""
    status: str = Field(..., description="Current status: uploaded, processing, completed, failed")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    message: str = Field(..., description="Human-readable status message (Hinglish)")
    stage: ProcessingStage = Field(..., description="Current processing stage")
    audio_url: Optional[str] = Field(None, description="URL to generated audio")
    duration: Optional[int] = Field(None, description="Audio duration in seconds")
    error: Optional[str] = Field(None, description="Error message if failed")


class ProcessingRequest(BaseModel):
    """Request to process a file"""
    subject: str = Field(default="General", description="Subject name")
    chapter: str = Field(default="Notes", description="Chapter or topic name")


class PodcastMetadata(BaseModel):
    """Metadata for a generated podcast"""
    job_id: str
    title: str
    original_file: str
    duration: int  # seconds
    created_at: str
    audio_file: str
    script: Optional[str] = None


class PodcastResponse(BaseModel):
    """Response containing podcast details"""
    job_id: str
    title: str
    audio_url: str
    duration: int
    created_at: datetime
    subject: str
    chapter: str


class LibraryResponse(BaseModel):
    """Response containing user's podcast library"""
    podcasts: List[PodcastMetadata]
    total: int


class UploadResponse(BaseModel):
    """Response after file upload"""
    job_id: str
    status: str
    message: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None


# Subject options for the frontend
SUBJECTS = [
    "Physics",
    "Chemistry", 
    "Biology",
    "Mathematics",
    "English",
    "Hindi",
    "History",
    "Geography",
    "Economics",
    "Political Science",
    "Computer Science",
    "General"
]

# Exam categories
EXAMS = [
    "JEE Main",
    "JEE Advanced",
    "NEET",
    "BITSAT",
    "VITEEE",
    "CBSE Board",
    "State Board",
    "CUET",
    "Other"
]
