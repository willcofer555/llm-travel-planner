import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.schemas import TripResponse, Location
from services.trip_service import trip_service

logger = logging.getLogger(__name__)
router = APIRouter()


class AddLocationRequest(BaseModel):
    location: Location
    trip_id: str = None


@router.get("/trip/{trip_id}", response_model=TripResponse)
@router.get("/trip", response_model=TripResponse)
async def get_trip(trip_id: str = None):
    """Get a trip by ID, or default trip"""
    try:
        trip = trip_service.get_trip(trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        return TripResponse(success=True, trip=trip)
    except Exception as e:
        logger.error(f"Get trip error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get trip")


@router.post("/trip/add-location", response_model=TripResponse)
async def add_location_to_trip(request: AddLocationRequest):
    """Add a location to a trip"""
    try:
        trip = trip_service.add_location_to_trip(request.location, request.trip_id)
        return TripResponse(success=True, trip=trip)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Add location error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add location to trip")


@router.delete("/trip/remove-location/{item_id}")
async def remove_location_from_trip(item_id: str, trip_id: str = None):
    """Remove a location from a trip"""
    try:
        trip = trip_service.remove_location_from_trip(item_id, trip_id)
        return TripResponse(success=True, trip=trip)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Remove location error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove location from trip")


@router.get("/trip/default/id")
async def get_default_trip_id():
    """Get the default trip ID"""
    return {"trip_id": trip_service.get_default_trip_id()}