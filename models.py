from sqlalchemy import Column, Integer, String, Boolean
from db import Base

class User(Base):
    """
    User model for the database.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # You could add relationships here later, e.g.:
    # articles = relationship("Article", back_populates="owner")
