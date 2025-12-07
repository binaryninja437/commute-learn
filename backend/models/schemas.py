"""
Pydantic schemas for API request/response models
Compatible with Pydantic v1
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ProcessingStage(str, Enum):
    UPLOAD = "upload"
    OCR = "ocr"
    SCRIPT = "script"
    TTS = "tts"
    DONE = "done"
    ERROR = "error"


class ProcessingStatus(BaseModel):
    status: str
    progress: int
    message: str
    stage: ProcessingStage
    audio_url: Optional[str] = None
    duration: Optional[int] = None
    error: Optional[str] = None


class ProcessingRequest(BaseModel):
    subject: str = "General"
    chapter: str = "Notes"


class PodcastMetadata(BaseModel):
    job_id: str
    title: str
    original_file: str
    duration: int
    created_at: str
    audio_file: str
    script: Optional[str] = None


class PodcastResponse(BaseModel):
    job_id: str
    title: str
    audio_url: str
    duration: int
    created_at: datetime
    subject: str
    chapter: str


class LibraryResponse(BaseModel):
    podcasts: List[PodcastMetadata]
    total: int


class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


SUBJECTS = [
    "Physics", "Chemistry", "Biology", "Mathematics",
    "English", "Hindi", "History", "Geography",
    "Economics", "Political Science", "Computer Science", "General"
]

EXAMS = [
    "JEE Main", "JEE Advanced", "NEET", "BITSAT",
    "VITEEE", "CBSE Board", "State Board", "CUET", "Other"
]
