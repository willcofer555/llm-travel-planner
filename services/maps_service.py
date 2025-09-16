import logging
from typing import List, Optional, Tuple
import googlemaps
from config import settings
from models.schemas import Location, AdditionalInfo, MapBounds


logger = logging.getLogger(__name__)


class GoogleMapsService:
    def __init__(self):
        self.client = googlemaps.Client(key=settings.google_maps_api_key)
    
    async def geocode_locations(self, locations: List[dict]) -> List[Location]:
        geocoded_locations = []
        
        for loc_data in locations:
            try:
                location = await self._geocode_single_location(loc_data)
                if location:
                    geocoded_locations.append(location)
            except Exception as e:
                logger.warning(f"Failed to geocode location {loc_data.get('name', 'Unknown')}: {str(e)}")
                continue
        
        return geocoded_locations
    
    async def _geocode_single_location(self, loc_data: dict) -> Optional[Location]:
        try:
            address = loc_data.get('address', '')
            name = loc_data.get('name', '')
            
            # First try Places API for more detailed info
            place_result = await self._search_place(name, address)
            if place_result:
                return self._create_location_from_place(loc_data, place_result)
            
            # Fallback to Geocoding API
            geocode_result = self.client.geocode(address)
            if geocode_result:
                return self._create_location_from_geocode(loc_data, geocode_result[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Geocoding error for {loc_data.get('name', 'Unknown')}: {str(e)}")
            return None
    
    async def _search_place(self, name: str, address: str) -> Optional[dict]:
        try:
            # Search for place by name and address
            query = f"{name} {address}"
            places_result = self.client.places(query=query)
            
            if places_result['results']:
                place_id = places_result['results'][0]['place_id']
                
                # Get detailed place information
                place_details = self.client.place(
                    place_id=place_id,
                    fields=['name', 'formatted_address', 'geometry', 'opening_hours', 
                           'price_level', 'rating', 'website', 'business_status', 'photo']
                )
                
                return place_details['result']
            
            return None
            
        except Exception as e:
            logger.warning(f"Places API search failed: {str(e)}")
            return None
    
    def _create_location_from_place(self, loc_data: dict, place_result: dict) -> Location:
        geometry = place_result.get('geometry', {})
        location_coords = geometry.get('location', {})
        
        # Extract additional info from Places API
        additional_info = AdditionalInfo()
        
        if 'opening_hours' in place_result:
            hours = place_result['opening_hours']
            if 'weekday_text' in hours and hours['weekday_text']:
                additional_info.opening_hours = hours['weekday_text'][0]  # Today's hours
        
        if 'price_level' in place_result:
            price_level = place_result['price_level']
            price_map = {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
            additional_info.price_range = price_map.get(price_level, "$$")
        
        if 'rating' in place_result:
            additional_info.rating = float(place_result['rating'])
        
        if 'website' in place_result:
            additional_info.website = place_result['website']
        
        # Get photo URL if available
        photo_url = None
        if 'photos' in place_result and place_result['photos']:
            photo_reference = place_result['photos'][0]['photo_reference']
            # Create photo URL (max width 200px for info cards)
            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=200&photoreference={photo_reference}&key={self.client.key}"
        
        return Location(
            name=loc_data['name'],
            description=loc_data['description'],
            category=loc_data['category'],
            address=place_result.get('formatted_address', loc_data['address']),
            lat=float(location_coords.get('lat', 0)),
            lng=float(location_coords.get('lng', 0)),
            additional_info=additional_info,
            photo_url=photo_url
        )
    
    def _create_location_from_geocode(self, loc_data: dict, geocode_result: dict) -> Location:
        geometry = geocode_result.get('geometry', {})
        location_coords = geometry.get('location', {})
        
        return Location(
            name=loc_data['name'],
            description=loc_data['description'],
            category=loc_data['category'],
            address=geocode_result.get('formatted_address', loc_data['address']),
            lat=float(location_coords.get('lat', 0)),
            lng=float(location_coords.get('lng', 0)),
            additional_info=None
        )
    
    def calculate_map_bounds(self, locations: List[Location]) -> Optional[MapBounds]:
        if not locations:
            return None
        
        lats = [loc.lat for loc in locations]
        lngs = [loc.lng for loc in locations]
        
        # Add padding to bounds
        padding = 0.01
        
        return MapBounds(
            north=max(lats) + padding,
            south=min(lats) - padding,
            east=max(lngs) + padding,
            west=min(lngs) - padding
        )