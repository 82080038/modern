"""
Educational Content dan Trading Journal Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum
from datetime import datetime, date

class ContentType(enum.Enum):
    """Content types"""
    VIDEO = "video"
    ARTICLE = "article"
    TUTORIAL = "tutorial"
    WEBINAR = "webinar"
    PODCAST = "podcast"
    EBOOK = "ebook"
    COURSE = "course"

class DifficultyLevel(enum.Enum):
    """Difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class JournalEntryType(enum.Enum):
    """Journal entry types"""
    TRADE = "trade"
    ANALYSIS = "analysis"
    LESSON = "lesson"
    REFLECTION = "reflection"
    GOAL = "goal"

class EducationalContent(Base):
    """Educational content"""
    __tablename__ = "educational_content"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Content details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(Enum(ContentType), nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    
    # Content data
    content_url = Column(String(500), nullable=True)
    content_text = Column(Text, nullable=True)
    content_duration = Column(Integer, nullable=True)  # minutes
    content_size = Column(Integer, nullable=True)  # bytes
    
    # Metadata
    tags = Column(JSON, nullable=True)
    category = Column(String(100), nullable=True)
    author = Column(String(100), nullable=True)
    language = Column(String(10), default="en")
    
    # Statistics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Settings
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TradingJournal(Base):
    """Trading journal entries"""
    __tablename__ = "trading_journal"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Entry details
    title = Column(String(200), nullable=False)
    entry_type = Column(Enum(JournalEntryType), nullable=False)
    content = Column(Text, nullable=False)
    
    # Trade specific data
    symbol = Column(String(20), nullable=True)
    trade_date = Column(Date, nullable=True)
    entry_price = Column(Float, nullable=True)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Integer, nullable=True)
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)
    
    # Analysis data
    analysis_data = Column(JSON, nullable=True)
    technical_indicators = Column(JSON, nullable=True)
    fundamental_analysis = Column(JSON, nullable=True)
    sentiment_analysis = Column(JSON, nullable=True)
    
    # Learning data
    lessons_learned = Column(Text, nullable=True)
    mistakes_made = Column(Text, nullable=True)
    improvements = Column(Text, nullable=True)
    
    # Tags and categories
    tags = Column(JSON, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class LearningPath(Base):
    """Learning paths"""
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Path details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    
    # Path structure
    content_order = Column(JSON, nullable=True)  # Ordered list of content IDs
    prerequisites = Column(JSON, nullable=True)
    learning_objectives = Column(JSON, nullable=True)
    
    # Statistics
    completion_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    estimated_duration = Column(Integer, nullable=True)  # hours
    
    # Settings
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserProgress(Base):
    """User learning progress"""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    content_id = Column(String(50), nullable=False, index=True)
    
    # Progress data
    progress_percent = Column(Float, default=0.0)
    time_spent = Column(Integer, default=0)  # minutes
    last_position = Column(Integer, default=0)  # seconds for videos
    
    # Completion
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Rating and feedback
    rating = Column(Integer, nullable=True)  # 1-5 stars
    feedback = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TradingGoals(Base):
    """Trading goals and objectives"""
    __tablename__ = "trading_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    
    # Goal details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    goal_type = Column(String(50), nullable=False)  # profit, learning, risk, etc.
    
    # Goal metrics
    target_value = Column(Float, nullable=True)
    current_value = Column(Float, default=0.0)
    unit = Column(String(20), nullable=True)  # USD, %, trades, etc.
    
    # Timeline
    start_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)
    is_achieved = Column(Boolean, default=False)
    achieved_at = Column(DateTime, nullable=True)
    
    # Progress tracking
    progress_updates = Column(JSON, nullable=True)
    milestones = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TradingAchievements(Base):
    """Trading achievements and badges"""
    __tablename__ = "trading_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    achievement_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Achievement details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    
    # Requirements
    requirements = Column(JSON, nullable=True)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    
    # Statistics
    earned_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserAchievements(Base):
    """User earned achievements"""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    achievement_id = Column(String(50), nullable=False, index=True)
    
    # Achievement data
    earned_at = Column(DateTime, nullable=False)
    progress_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TradingQuiz(Base):
    """Trading knowledge quizzes"""
    __tablename__ = "trading_quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Quiz details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    
    # Quiz content
    questions = Column(JSON, nullable=True)
    time_limit = Column(Integer, nullable=True)  # minutes
    passing_score = Column(Float, default=70.0)  # percentage
    
    # Statistics
    attempt_count = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    
    # Settings
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class QuizAttempts(Base):
    """Quiz attempt records"""
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    quiz_id = Column(String(50), nullable=False, index=True)
    
    # Attempt data
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    time_taken = Column(Integer, nullable=True)  # seconds
    
    # Results
    answers = Column(JSON, nullable=True)
    is_passed = Column(Boolean, default=False)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
