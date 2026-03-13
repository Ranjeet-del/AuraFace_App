from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict
from datetime import date, datetime, timedelta
import random

from app.database import get_db
from app.models import User, ChatMessage
from app.models_quiz import QuizQuestion, DailyQuiz, QuizAttempt, UserGamification, RewardItem, RedeemedReward
from app.schemas_quiz import QuestionResponse, QuizAttemptSubmit, QuizResultResponse, GamificationProfile, LeaderboardEntry, RewardItemOut, RedeemRequest, RedeemedRewardOut, DuelWagerCreate, FocusSessionSubmit
from app.utils.websocket_manager import manager
import asyncio
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
        attachment_url=question.attachment_url,
        options=question.options,
        correct_option_index=question.correct_option_index,
        explanation=question.explanation
    )
    db.commit()
    db.refresh(new_q)
    return new_q

# --- Utilities ---
import os
import shutil
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    safe_filename = f"{datetime.now().timestamp()}_{file.filename.replace(' ', '_')}"
    file_location = f"images/quiz/{safe_filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": f"/{file_location}", "filename": file.filename}

# --- Focus Flow (Pomodoro) ---

@router.post("/focus/submit")
def submit_focus_session(
    req: FocusSessionSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if req.duration_minutes <= 0:
        raise HTTPException(status_code=400, detail="Duration must be positive")
        
    # Calculate XP (e.g. 5 XP per minute)
    xp_earned = req.duration_minutes * 5
    
    # Optional logic: Cap daily Focus XP or give streak multipliers.
    profile = db.query(UserGamification).filter(UserGamification.user_id == current_user.id).first()
    if not profile:
        profile = UserGamification(user_id=current_user.id)
        db.add(profile)
        
    profile.total_xp += xp_earned
    
    # Check for level up
    old_level = profile.current_level
    while profile.total_xp >= (profile.current_level * 1000):
        profile.current_level += 1
        
    db.commit()
    
    return {
        "message": f"Awesome focus! You studied {req.subject_tag} for {req.duration_minutes}m.",
        "xp_earned": xp_earned,
        "new_total_xp": profile.total_xp,
        "level_up": profile.current_level > old_level
    }

# --- Rewards Store ---

@router.get("/rewards", response_model=List[RewardItemOut])
def get_rewards(db: Session = Depends(get_db)):
    # Optional: seed some rewards if table is empty
    if db.query(RewardItem).count() == 0:
        default_rewards = [
            RewardItem(title="Premium Resume Template", description="Unlock a professionally designed IT resume.", xp_cost=500, icon_name="Description", bg_color="0xFFE2E8F0"),
            RewardItem(title="1-on-1 Mock Interview", description="Virtual mock interview with Ask Aura AI.", xp_cost=2000, icon_name="Mic", bg_color="0xFFFEF3C7"),
            RewardItem(title="Priority Placement Drive", description="Get top-list priority for the next campus drive.", xp_cost=5000, icon_name="Work", bg_color="0xFFD1FAE5"),
            RewardItem(title="Campus Cafe Voucher", description="Rs. 50 OFF at the Campus Canteen", xp_cost=1500, icon_name="Coffee", bg_color="0xFFFFEDD5")
        ]
        db.add_all(default_rewards)
        db.commit()
        
    return db.query(RewardItem).filter(RewardItem.is_active == True).all()

@router.post("/rewards/redeem", response_model=RedeemedRewardOut)
def redeem_reward(
    req: RedeemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reward = db.query(RewardItem).filter(RewardItem.id == req.reward_id, RewardItem.is_active == True).first()
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
        
    if reward.stock == 0:
        raise HTTPException(status_code=400, detail="Reward out of stock")
        
    profile = db.query(UserGamification).filter(UserGamification.user_id == current_user.id).first()
    if not profile or profile.total_xp < reward.xp_cost:
        raise HTTPException(status_code=400, detail="Not enough XP to redeem this reward")
        
    # Deduct XP
    profile.total_xp -= reward.xp_cost
    
    if reward.stock > 0:
        reward.stock -= 1
        
    redeemed = RedeemedReward(
        user_id=current_user.id,
        reward_id=reward.id,
        status="PENDING"
    )
    
    db.add(redeemed)
    db.commit()
    db.refresh(redeemed)
    return redeemed

@router.get("/rewards/my", response_model=List[RedeemedRewardOut])
def get_my_rewards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(RedeemedReward).filter(RedeemedReward.user_id == current_user.id).order_by(desc(RedeemedReward.redeemed_at)).all()

# --- Quiz Duels (Chat Integaration) ---

@router.post("/duel/invite")
async def send_duel_invite(
    req: DuelWagerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify Sender XP
    sender_profile = db.query(UserGamification).filter(UserGamification.user_id == current_user.id).first()
    if not sender_profile or sender_profile.total_xp < req.wager_amount:
         raise HTTPException(status_code=400, detail="You do not have enough XP to wager this amount.")
         
    target = db.query(User).filter(User.id == req.target_user_id).first()
    if not target:
         raise HTTPException(status_code=404, detail="Target user not found")
         
    # Form Direct Message Group ID
    u1, u2 = sorted([current_user.id, target.id])
    group_id = f"DM_{u1}_{u2}"
    
    # Extract 5 Random Questions from the DB for the Duel
    q_query = db.query(QuizQuestion.id)
    if req.category != "MIXED":
        q_query = q_query.filter(QuizQuestion.category == req.category)
    q_ids_tuples = q_query.order_by(func.random()).limit(5).all()
    q_ids = [q[0] for q in q_ids_tuples]
    
    if len(q_ids) < 5:
        raise HTTPException(status_code=400, detail="Not enough questions in this category to start a duel.")
        
    duel_state = {
         "type": "DUEL_INVITE",
         "wager": req.wager_amount,
         "category": req.category,
         "questions": q_ids,
         "challenger_id": current_user.id,
         "challenger_score": None,
         "target_id": target.id,
         "target_score": None,
         "status": "PENDING"
    }
    
    import json
    msg_content = json.dumps(duel_state)
    
    # Save the Duel as a special Chat Message
    duel_msg = ChatMessage(
         sender_id=current_user.id,
         group_id=group_id,
         content=msg_content,
         msg_type="DUEL",
         timestamp=datetime.utcnow()
    )
    
    db.add(duel_msg)
    
    # Deduct XP temporarily (Escrow)
    sender_profile.total_xp -= req.wager_amount
    
    db.commit()
    db.refresh(duel_msg)
    
    # Broadcast to websocket
    msg_data = {
         "id": duel_msg.id,
         "sender_id": current_user.id,
         "sender_name": current_user.full_name or current_user.username,
         "sender_profile_image": current_user.profile_image,
         "group_id": group_id,
         "content": msg_content,
         "msg_type": "DUEL",
         "timestamp": duel_msg.timestamp.isoformat(),
         "status": "DELIVERED"
    }
    
    await manager.broadcast_to_group(msg_data, group_id)
    
    return {"message": "Duel invite sent!", "duel_id": duel_msg.id}

