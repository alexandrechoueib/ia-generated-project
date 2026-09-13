"""Modèles Pydantic pour l'API de débat."""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Complexity(str, Enum):
    TOUT_PUBLIC = "tout_public"
    INTERMEDIAIRE = "intermediaire"
    EXPERT = "expert"


class Speaker(str, Enum):
    GROK = "grok"
    GPT = "gpt"
    SUMMARY = "summary"


class DebateCreate(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    total_messages: int = Field(..., ge=2, le=20)
    complexity: Complexity = Complexity.TOUT_PUBLIC

    @field_validator("total_messages")
    @classmethod
    def must_be_even(cls, v: int) -> int:
        if v % 2 != 0:
            raise ValueError("total_messages doit être pair (entre 2 et 20).")
        return v


class Message(BaseModel):
    index: int
    speaker: Speaker
    content: str
    side: Optional[Literal["pour", "contre", "neutre"]] = None


class DebateStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Debate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    topic: str
    total_messages: int
    complexity: Complexity
    status: DebateStatus = DebateStatus.CREATED
    messages: list[Message] = Field(default_factory=list)
    summary: Optional[str] = None
    error: Optional[str] = None

    @property
    def remaining_turns(self) -> int:
        spoken = sum(1 for m in self.messages if m.speaker in (Speaker.GROK, Speaker.GPT))
        return max(0, self.total_messages - spoken)


class DebateCreateResponse(BaseModel):
    id: str
    topic: str
    total_messages: int
    complexity: Complexity
    status: DebateStatus


class DebateResponse(BaseModel):
    id: str
    topic: str
    total_messages: int
    complexity: Complexity
    status: DebateStatus
    messages: list[Message]
    summary: Optional[str] = None
    remaining_turns: int
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str
