from pydantic import BaseModel
from typing import List
from enum import Enum

class ProcessingStatus(str, Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    ERROR = "error"

class ArchitecturalComponent(BaseModel):
    name: str
    type: str
    description: str

class ArchitecturalRisk(BaseModel):
    severity: str  # low, medium, high
    description: str

class ArchitecturalRecommendation(BaseModel):
    priority: str  # low, medium, high
    description: str

class AnalysisReport(BaseModel):
    components: List[ArchitecturalComponent]
    risks: List[ArchitecturalRisk]
    recommendations: List[ArchitecturalRecommendation]
    summary: str

class AnalysisResponse(BaseModel):
    status: ProcessingStatus
    report: AnalysisReport | None = None
    error: str | None = None
