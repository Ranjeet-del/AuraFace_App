from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict
from datetime import date, datetime, timedelta
import random

from app.database import get_db
from app.models import User
from app.models_quiz import QuizQuestion, DailyQuiz, QuizAttempt, UserGamification
from app.schemas_quiz import QuestionResponse, QuizAttemptSubmit, QuizResultResponse, GamificationProfile, LeaderboardEntry
from app.auth_dependencies import get_current_active_user as get_current_user
from app.firebase_utils import send_topic_notification 

router = APIRouter(prefix="/quiz", tags=["Gamification Quiz"])

# --- Levels Configuration ---
LEVEL_THRESHOLDS = {
    1: 200,   # Beginner
    2: 600,   # Intermediate 
    3: 1200,  # Advanced
    4: 1000000 # Elite (Target for max level)
}

LEVEL_TITLES = {
    1: "Beginner",
    2: "Intermediate",
    3: "Advanced",
    4: "Elite"
}

def get_level_info(xp: int):
    current_level = 1
    for level, threshold in LEVEL_THRESHOLDS.items():
        if xp >= threshold:
            current_level = level + 1 if level < 4 else 4
        else:
            break
            
    # Calculate progress to next level
    prev_threshold = LEVEL_THRESHOLDS.get(current_level - 1, 0) if current_level > 1 else 0
    next_threshold = LEVEL_THRESHOLDS.get(current_level, LEVEL_THRESHOLDS[4])
    
    if current_level == 4:
        progress = 1.0
    else:
        needed = next_threshold - prev_threshold
        current = xp - prev_threshold
        progress = max(0.0, min(1.0, current / needed))
        
    return current_level, LEVEL_TITLES.get(current_level, "Elite"), next_threshold, progress

@router.get("/daily", response_model=List[QuestionResponse])
def get_daily_quiz(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Check if user already attempted today
    today = date.today()
    existing_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.quiz_date == today
    ).first()
    
    if existing_attempt:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You have already attempted the daily quiz today."
        )

    # 2. Get or Create Daily Quiz
    daily_quiz = db.query(DailyQuiz).filter(DailyQuiz.date == today).first()
    
    if not daily_quiz:
        # Generate new quiz
        # Distribution: 12 Subject, 4 Aptitude, 2 College, 2 Fun
        questions = []
        
        # Check if we have any questions in DB at all
        total_q_count = db.query(QuizQuestion).count()
        if total_q_count == 0:
             # Seed on the fly
             seed_dummy_questions(db)
        
        # Helper to fetch random questions
        def fetch_random(category, count):
            qs = db.query(QuizQuestion).filter(QuizQuestion.category == category).all()
            if len(qs) <= count:
                return qs
            return random.sample(qs, count)

        questions.extend(fetch_random("SUBJECT", 12))
        questions.extend(fetch_random("APTITUDE", 4))
        questions.extend(fetch_random("COLLEGE", 2))
        questions.extend(fetch_random("FUN", 2))
        
        # Determine IDs
        q_ids = [q.id for q in questions]
        
        # Fallback if DB is empty, try to get *any* questions
        if len(q_ids) < 20: 
             all_qs = db.query(QuizQuestion).all()
             # If strictly need 20, fill with randoms from available
             needed = 20 - len(q_ids)
             if all_qs:
                 extras = random.choices(all_qs, k=needed)
                 q_ids.extend([q.id for q in extras])
        
        # Save
        daily_quiz = DailyQuiz(date=today, question_ids=q_ids)
        db.add(daily_quiz)
        db.commit()
        db.refresh(daily_quiz)
        
        # Send Notification (Background)
        background_tasks.add_task(
            send_topic_notification,
            topic="daily_quiz",
            title="Daily Quiz is Live! 🧠",
            body="New questions are ready. Can you top the leaderboard today?"
        )

    # 3. Fetch Question Objects
    if not daily_quiz.question_ids:
        return []

    # Ensure IDs are unique and exist
    question_objects = db.query(QuizQuestion).filter(QuizQuestion.id.in_(daily_quiz.question_ids)).all()
    
    # Sort to match the random order in daily_quiz if needed, or shuffle
    random.shuffle(question_objects)
    
    return question_objects

@router.post("/submit", response_model=QuizResultResponse)
def submit_quiz_attempt(
    submission: QuizAttemptSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    
    # Check double submission
    existing = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.quiz_date == today
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already submitted today")
    
    # Authenticate Questions
    daily_quiz = db.query(DailyQuiz).filter(DailyQuiz.date == today).first()
    if not daily_quiz:
        raise HTTPException(status_code=404, detail="No daily quiz found")
        
    questions = db.query(QuizQuestion).filter(QuizQuestion.id.in_(daily_quiz.question_ids)).all()
    q_map = {q.id: q for q in questions}
    
    score = 0
    correct_answers = {}
    explanations = {}
    
    for q_id, answer_idx in submission.answers.items():
        if q_id in q_map:
            q = q_map[q_id]
            correct_answers[q_id] = q.correct_option_index
            explanations[q_id] = q.explanation or "No explanation provided."
            
            if answer_idx == q.correct_option_index:
                score += 1
    
    # Logic for XP and Streak
    user_profile = db.query(UserGamification).filter(UserGamification.user_id == current_user.id).first()
    if not user_profile:
        user_profile = UserGamification(user_id=current_user.id, total_xp=0, current_streak=0)
        db.add(user_profile)
    
    # Streak Logic
    streak_bonus = 0
    if user_profile.last_quiz_date == today - timedelta(days=1):
        user_profile.current_streak += 1
    elif user_profile.last_quiz_date == today:
        pass # Should not happen due to check above
    else:
        user_profile.current_streak = 1 # Reset or first time
        
    # Streak Multipliers (3-day, 7-day, 15-day)
    streak_mult = 1.0
    if user_profile.current_streak >= 15:
        streak_mult = 2.0
        streak_bonus = 50
    elif user_profile.current_streak >= 7:
        streak_mult = 1.5
        streak_bonus = 25
    elif user_profile.current_streak >= 3:
        streak_mult = 1.2
        streak_bonus = 10
        
    # XP Calculation (Base 10 per question)
    question_xp = score * 10
    total_xp_earned = int(question_xp * streak_mult) + streak_bonus
    
    # Update Profile
    user_profile.total_xp += total_xp_earned
    user_profile.last_quiz_date = today
    
    # Level Up Check
    current_level_calc, level_title, next_threshold, current_progress = get_level_info(user_profile.total_xp)
    if current_level_calc > user_profile.current_level:
        # leveled up!
        user_profile.current_level = current_level_calc
    
    # Save Attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_date=today,
        score=score,
        xp_earned=total_xp_earned,
        answers_json=submission.answers,
        time_taken_seconds=submission.time_taken_seconds
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(user_profile)
    
    return QuizResultResponse(
        score=score,
        total_questions=len(questions),
        xp_earned=total_xp_earned,
        new_total_xp=user_profile.total_xp,
        new_level=user_profile.current_level,
        streak_bonus=streak_bonus,
        next_level_xp=next_threshold,
        progress=current_progress,
        correct_answers=correct_answers,
        explanations=explanations
    )

@router.get("/profile", response_model=GamificationProfile)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(UserGamification).filter(UserGamification.user_id == current_user.id).first()
    if not profile:
        # Create default
        profile = UserGamification(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
    lvl, title, next_xp, progress = get_level_info(profile.total_xp)
    
    return GamificationProfile(
        user_id=current_user.id,
        total_xp=profile.total_xp,
        current_level=lvl,
        current_streak=profile.current_streak,
        badges=profile.badges,
        title=title,
        next_level_xp=next_xp,
        progress=progress
    )

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(
    limit: int = 10,
    period: str = "all_time", # daily, weekly, monthly, all_time
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(UserGamification, User).join(User, UserGamification.user_id == User.id)
    
    if period == "daily":
        # Complex join with attempts
        # For simplicity, let"s just do all-time XP for now as per "Global Leaderboard" standard
        pass
        
    results = query.order_by(desc(UserGamification.total_xp)).limit(limit).all()
    
    leaderboard = []
    for rank, (gamification, user) in enumerate(results, 1):
        leaderboard.append(LeaderboardEntry(
            rank=rank,
            username=user.username,
            full_name=user.full_name or user.username,
            total_xp=gamification.total_xp,
            badges=gamification.badges
        ))
        
    return leaderboard

@router.post("/seed_dummy", include_in_schema=True) # Explicitly keep for testing
def seed_dummy_questions(db: Session = Depends(get_db)):
    # ... (existing content) ...
    # Seed 50 questions if empty
    if db.query(QuizQuestion).count() > 0:
        return {"message": "Questions already exist"}
        
    import json
    
    categories = ["SUBJECT", "APTITUDE", "COLLEGE", "FUN"]
    
    new_questions = []
    for i in range(50):
        cat = categories[i % 4]
        q = QuizQuestion(
            category=cat,
            subcategory="General",
            difficulty="MEDIUM",
            question_text=f"Sample Question {i+1} regarding {cat}?",
            options=["Option A", "Option B", "Option C", "Option D"],
            correct_option_index=0,
            explanation="This is a dummy explanation."
        )
        new_questions.append(q)
        
    db.add_all(new_questions)
    db.commit()
    return {"message": "Seeded 50 dummy questions"}

from app.schemas_quiz import QuestionCreate
@router.post("/question", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only Admin or Teacher should be allowed ideally, but for now open to authenticated users or check role
    # if current_user.role not in ["admin", "teacher"]:
    #     raise HTTPException(status_code=403, detail="Not authorized")
        
    new_q = QuizQuestion(
        category=question.category,
        subcategory=question.subcategory,
        difficulty=question.difficulty,
        question_text=question.question_text,
        options=question.options,
        correct_option_index=question.correct_option_index,
        explanation=question.explanation
    )
    db.add(new_q)
    db.commit()
    db.refresh(new_q)
    return new_q
