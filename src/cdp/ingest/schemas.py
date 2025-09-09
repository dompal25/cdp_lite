from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Identify(BaseModel):
    userId: Optional[str] = Field(default=None, alias="user_id")
    anonymousId: Optional[str] = Field(default=None, alias="anonymous_id")
    traits: Dict[str, Any] = {}
    timestamp: Optional[str] = None

class Track(BaseModel):
    userId: Optional[str] = Field(default=None, alias="user_id")
    anonymousId: Optional[str] = Field(default=None, alias="anonymous_id")
    event: str
    properties: Dict[str, Any] = {}
    timestamp: Optional[str] = None
