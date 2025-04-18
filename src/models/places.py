import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Float,
    ForeignKey,
    UniqueConstraint,
    Text,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from db.database import NewBase as Base
from schemas.places import BasePlaceResponse


class Place(Base):
    __tablename__ = 'places'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    place_id = Column(String(255), unique=True, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    display_name = Column(Text)
    place_class = Column(String(255))
    place_type = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint('lat BETWEEN -90.0 AND 90.0', name='ck_places_lat_range'),
        CheckConstraint('lon BETWEEN -180.0 AND 180.0', name='ck_places_lon_range'),
    )

    @classmethod
    def from_schema(cls, place: 'BasePlaceResponse') -> 'Place':
        return cls(
            place_id=place.place_id,
            lat=place.lat,
            lon=place.lon,
            display_name=place.display_name,
            place_class=place.place_class,
            place_type=place.place_type,
        )

    def __repr__(self) -> str:
        return f'<Place {self.id}>'


class SearchHistory(Base):
    __tablename__ = 'search_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    place_id = Column(String, ForeignKey('places.place_id'), nullable=False)
    search_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('user_id', 'place_id', name='search_history_user_place_unique'),
    )

    def __repr__(self) -> str:
        return f'<SearchHistory {self.id}>'


class FavoritePlace(Base):
    __tablename__ = 'favorite_places'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    place_id = Column(String, ForeignKey('places.place_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('user_id', 'place_id', name='favorite_places_user_place_unique'),
    )

    def __repr__(self) -> str:
        return f'<FavoritePlace {self.id}>'
