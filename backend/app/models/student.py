from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    cgpa = Column(Float, nullable=True)
    department = Column(String, nullable=True)
    resume_path = Column(String, nullable=True)
    resume_text = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=True)  # extracted skills, education, etc.

    user = relationship("User", backref="student_profile")
