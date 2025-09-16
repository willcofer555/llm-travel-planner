from typing import Dict, Optional
from datetime import datetime
import uuid
from models.schemas import Trip, TripItem, Location


class TripService:
    def __init__(self):
        # Simple in-memory storage (would be database in production)
        self.trips: Dict[str, Trip] = {}
        self.default_trip_id = self._create_default_trip()
    
    def _create_default_trip(self) -> str:
        """Create a default trip for users"""
        trip_id = str(uuid.uuid4())
        self.trips[trip_id] = Trip(
            id=trip_id,
            name="My Trip",
            created_at=datetime.now(),
            items=[]
        )
        return trip_id
    
    def get_trip(self, trip_id: Optional[str] = None) -> Optional[Trip]:
        """Get trip by ID, or default trip if no ID provided"""
        if trip_id is None:
            trip_id = self.default_trip_id
        return self.trips.get(trip_id)
    
    def add_location_to_trip(self, location: Location, trip_id: Optional[str] = None) -> Trip:
        """Add a location to a trip"""
        if trip_id is None:
            trip_id = self.default_trip_id
        
        trip = self.trips.get(trip_id)
        if not trip:
            raise ValueError(f"Trip {trip_id} not found")
        
        # Check if location already exists in trip
        for item in trip.items:
            if item.location.name == location.name and item.location.address == location.address:
                return trip  # Already exists, don't add duplicate
        
        # Add new trip item
        trip_item = TripItem(
            id=str(uuid.uuid4()),
            location=location,
            added_at=datetime.now()
        )
        
        trip.items.append(trip_item)
        return trip
    
    def remove_location_from_trip(self, item_id: str, trip_id: Optional[str] = None) -> Trip:
        """Remove a location from a trip"""
        if trip_id is None:
            trip_id = self.default_trip_id
            
        trip = self.trips.get(trip_id)
        if not trip:
            raise ValueError(f"Trip {trip_id} not found")
        
        trip.items = [item for item in trip.items if item.id != item_id]
        return trip
    
    def get_default_trip_id(self) -> str:
        """Get the default trip ID"""
        return self.default_trip_id


# Global instance
trip_service = TripService()