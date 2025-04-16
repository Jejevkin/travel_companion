from datetime import datetime

from pydantic import BaseModel, Field, UUID4


class BaseCoordinates(BaseModel):
    lat: float = Field(..., description='Latitude')
    lon: float = Field(..., description='Longitude')


class BasePlaceResponse(BaseCoordinates):
    place_id: str
    display_name: str
    place_class: str | None = Field(default=None, alias='class')
    place_type: str | None = Field(default=None, alias='type')


class SearchPlaceRequest(BaseModel):
    query: str = Field(..., description='Search query')
    limit: int = Field(10, ge=1, le=50, description='Maximum number of results')

    def to_params(self, api_key: str):
        return {
            'key': api_key,
            'q': self.query,
            'format': 'json',
        }


class SearchPlaceResponse(BasePlaceResponse):
    importance: float | None = None


class NearbyPlaceRequest(BaseCoordinates):
    tags: list[str] | None = Field(default_factory=list,
                                   description='Search tag or advanced tags. Example: \'amenity:* or !amenity:gym\'')
    radius: int = Field(500, ge=100, le=5000, description='Search radius in meters')
    limit: int = Field(10, ge=1, le=50, description='Maximum number of results')

    def to_params(self, api_key: str):
        return {
            'key': api_key,
            'lat': self.lat,
            'lon': self.lon,
            'tag': ','.join(self.tags),
            'radius': self.radius,
            'limit': self.limit,
            'format': 'json',
        }


class NearbyPlaceResponse(BasePlaceResponse):
    name: str | None = 'No name'
    distance: float | None = None


class FavoritePlaceCreate(BaseModel):
    place_id: str = Field(..., description='Place ID')


class FavoritePlaceResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    place_id: str
    created_at: datetime
