import json
import logging
from typing import List, Optional, Tuple
from openai import AsyncOpenAI
from config import settings
from models.schemas import Location, LocationCategory


logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.system_prompt = """You are an expert travel assistant. When users ask about places to visit, respond with a conversational message AND provide structured location data.

Requirements:
1. Provide 3-5 specific location recommendations
2. Include exact addresses for geocoding
3. Write engaging descriptions (50-100 words each)
4. Categorize each location (museum, restaurant, landmark, activity, shopping)
5. Consider user's interests and travel style

Response format: JSON with 'chat_response' and 'locations' array. Each location must have: name, description, category, address.
Example categories: museum, restaurant, landmark, activity, shopping, other"""

    async def get_travel_recommendations(
        self, 
        user_message: str, 
        city: Optional[str] = None,
        context: Optional[dict] = None
    ) -> Tuple[str, List[dict]]:
        try:
            user_context = f"Current city: {city or 'Not specified'}\n"
            if context and context.get('previous_locations'):
                user_context += f"Previous recommendations: {len(context['previous_locations'])} locations\n"
            
            prompt = f"{user_context}User question: {user_message}\n\nProvide travel recommendations in JSON format."
            
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
            )
            
            content = response.choices[0].message.content
            logger.info(f"OpenAI raw response: {content}")
            
            # Try to parse as JSON
            try:
                data = json.loads(content)
                chat_response = data.get('chat_response', '')
                locations = data.get('locations', [])
                
                # Validate and clean locations
                valid_locations = []
                for loc in locations:
                    if self._validate_location(loc):
                        valid_locations.append(loc)
                    else:
                        logger.warning(f"Invalid location data: {loc}")
                
                return chat_response, valid_locations
                
            except json.JSONDecodeError:
                # Fallback: treat entire response as chat_response
                logger.warning("Failed to parse JSON from OpenAI response")
                return content, []
            
        except Exception as e:
            logger.error(f"OpenAI service error: {str(e)}")
            raise Exception(f"Failed to get AI recommendations: {str(e)}")
    
    def _validate_location(self, location: dict) -> bool:
        required_fields = ['name', 'description', 'category', 'address']
        if not all(field in location for field in required_fields):
            return False
        
        # Validate category
        valid_categories = ['museum', 'restaurant', 'landmark', 'activity', 'shopping', 'other']
        if location['category'] not in valid_categories:
            location['category'] = 'other'
        
        return True