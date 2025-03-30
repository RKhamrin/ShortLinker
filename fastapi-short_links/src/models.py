from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(UUID, primary_key=True, index=True)
    user_id = Column(Integer)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)

    linkings = relationship("Linking", back_populates="user")

class Linking(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    long_link = Column(String, nullable=False)
    custom_alias = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True))
    last_usage = Column(DateTime(timezone=True))
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    number_of_usages = Column(Integer, nullable=False)
    is_authorized = Column(Boolean, nullable=False)

    linkings = relationship("User", back_populates="links")