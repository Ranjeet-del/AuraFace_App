from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, JSON, DateTime, Float
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, date
from app.models import User

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)  # SUBJECT, APTITUDE, COLLEGE, FUN
    subcategory = Column(String, nullable=True) # DSA, Java, etc.
    difficulty = Column(String, default="MEDIUM") # EASY, MEDIUM, HARD
    question_text = Column(String, nullable=False)
    options = Column(JSON, nullable=False) # List of strings ["Option A", "Option B", ...]
    correct_option_index = Column(Integer, nullable=False) # 0-3
    explanation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DailyQuiz(Base):
    __tablename__ = "daily_quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, default=date.today)
    question_ids = Column(JSON, nullable=False) # List of 20 Question IDs
    created_at = Column(DateTime, default=datetime.utcnow)

class UserGamification(Base):
    __tablename__ = "user_gamification"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    total_xp = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    last_quiz_date = Column(Date, nullable=True)
    badges = Column(JSON, default=list) # List of badge strings or objects
    
    user = relationship("User")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_date = Column(Date, index=True)
    score = Column(Integer) # Number of correct answers
    xp_earned = Column(Integer)
    answers_json = Column(JSON) # User's answers map {q_id: selected_index}
    completed_at = Column(DateTime, default=datetime.utcnow)
    time_taken_seconds = Column(Integer, default=0)
    
    user = relationship("User")
