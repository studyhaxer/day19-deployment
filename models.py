from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column (String)
    role = Column (String, nullable=False, default="student")
    courses = relationship("Course", back_populates="owner", cascade="all, delete-orphan")
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id')) # FK!
    # Many Courses -> One User
    owner = relationship("User", back_populates="courses")    