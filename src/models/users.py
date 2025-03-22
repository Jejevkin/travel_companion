import uuid
from datetime import datetime

from db.database import NewBase as Base
from schemas.users import UserCreate
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash


class User(Base):
    __tablename__ = 'users_database'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    @classmethod
    def from_schema(cls, user: 'UserCreate') -> 'User':
        return cls(
            login=user.login,
            password=generate_password_hash(user.password),
            first_name=user.first_name,
            last_name=user.last_name
        )

    def __repr__(self) -> str:
        return f'<User {self.login}>'
