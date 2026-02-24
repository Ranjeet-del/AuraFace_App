from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date, datetime

class QuestionBase(BaseModel):
    category: str
    subcategory: Optional[str] = None
    difficulty: str
    question_text: str
    options: List[str]
    # explanation removed from base to avoid leaking

class QuestionCreate(QuestionBase):
    correct_option_index: int
    explanation: Optional[str] = None

# New Schema for Single Question
class QuestionCreateRequest(QuestionCreate):
    pass

class QuestionResponse(QuestionBase):
    id: int
    
    class Config:
        orm_mode = True

class QuizAttemptSubmit(BaseModel):
    answers: Dict[int, int] # {question_id: selected_index}
    time_taken_seconds: int

class QuizResultResponse(BaseModel):
    score: int
    total_questions: int
    xp_earned: int
    new_total_xp: int
    new_level: int
    streak_bonus: int
    next_level_xp: int
    progress: float
    correct_answers: Dict[int, int] # {question_id: correct_index}
    explanations: Dict[int, str] # {question_id: explanation}
    
class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    full_name: str
    total_xp: int
    badges: List[str]

class GamificationProfile(BaseModel):
    user_id: int
    total_xp: int
    current_level: int
    current_streak: int
    badges: List[str]
    title: str # Beginner, Intermediate, etc.
    next_level_xp: int
    progress: float # 0.0 to 1.0 for progress bar
    
    class Config:
        orm_mode = True
