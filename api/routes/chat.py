import logging
from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse, ErrorResponse
from services.openai_service import OpenAIService
from services.maps_service import GoogleMapsService

logger = logging.getLogger(__name__)
router = APIRouter()

openai_service = OpenAIService()
maps_service = GoogleMapsService()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Chat request: {request.message[:100]}...")
        
        # Get AI recommendations
        chat_response, location_data = await openai_service.get_travel_recommendations(
            user_message=request.message,
            city=request.city,
            context=request.context
        )
        
        if not chat_response:
            raise HTTPException(status_code=500, detail="Failed to generate AI response")
        
        # Geocode locations if any were provided
        locations = []
        map_bounds = None
        
        if location_data:
            try:
                locations = await maps_service.geocode_locations(location_data)
                if locations:
                    map_bounds = maps_service.calculate_map_bounds(locations)
            except Exception as e:
                logger.warning(f"Geocoding failed: {str(e)}")
                # Continue with chat response even if geocoding fails
        
        return ChatResponse(
            success=True,
            chat_response=chat_response,
            locations=locations,
            map_bounds=map_bounds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process request"
        )