from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


LocationCategory = Literal['museum', 'restaurant', 'landmark', 'activity', 'shopping', 'other']


class AdditionalInfo(BaseModel):
    opening_hours: Optional[str] = None
    price_range: Optional[str] = None
    estimated_visit_time: Optional[str] = None
    rating: Optional[float] = Field(None, ge=1, le=5)
    website: Optional[str] = None


class Location(BaseModel):
    name: str
    description: str
    category: LocationCategory
    address: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    additional_info: Optional[AdditionalInfo] = None
    photo_url: Optional[str] = None


class ChatMessage(BaseModel):
    id: str
    type: Literal['user', 'assistant', 'system']
    content: str
    timestamp: datetime
    locations: Optional[List[Location]] = None


class MapBounds(BaseModel):
    north: float
    south: float
    east: float
    west: float


class ChatRequest(BaseModel):
    message: str = Field(..., max_length=500)
    city: Optional[str] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    chat_response: str
    locations: List[Location]
    map_bounds: Optional[MapBounds] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None


# Trip models
class TripItem(BaseModel):
    id: str
    location: Location
    added_at: datetime
    notes: Optional[str] = None


class Trip(BaseModel):
    id: str
    name: str
    created_at: datetime
    items: List[TripItem] = []
    
    
class TripResponse(BaseModel):
    success: bool
    trip: Trip