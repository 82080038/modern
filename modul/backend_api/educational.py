"""
Educational Content API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import date
from app.database import get_db
from app.services.educational_service import EducationalService
from app.models.educational import ContentType, DifficultyLevel, JournalEntryType
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/educational", tags=["Educational Content"])

# Pydantic schemas
class CreateEducationalContentRequest(BaseModel):
    title: str
    content_type: str  # video, article, tutorial, webinar, podcast, ebook, course
    difficulty_level: str  # beginner, intermediate, advanced, expert
    description: Optional[str] = None
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    content_duration: Optional[int] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    author: Optional[str] = None
    language: str = "en"

class CreateTradingJournalRequest(BaseModel):
    title: str
    entry_type: str  # trade, analysis, lesson, reflection, goal
    content: str
    symbol: Optional[str] = None
    trade_date: Optional[date] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    quantity: Optional[int] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    analysis_data: Optional[Dict] = None
    lessons_learned: Optional[str] = None
    mistakes_made: Optional[str] = None
    improvements: Optional[str] = None
    tags: Optional[List[str]] = None

class CreateLearningPathRequest(BaseModel):
    name: str
    description: Optional[str] = None
    difficulty_level: str = "beginner"
    content_order: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    estimated_duration: Optional[int] = None

class CreateTradingGoalRequest(BaseModel):
    title: str
    goal_type: str
    target_value: float
    unit: str
    start_date: date
    target_date: date
    description: Optional[str] = None

class CreateQuizRequest(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty_level: str = "beginner"
    questions: Optional[List[Dict]] = None
    time_limit: Optional[int] = None
    passing_score: float = 70.0

class SubmitQuizAttemptRequest(BaseModel):
    quiz_id: str
    answers: List[Dict]
    time_taken: Optional[int] = None

@router.post("/content/create")
async def create_educational_content(
    content_request: CreateEducationalContentRequest,
    db: Session = Depends(get_db)
):
    """Create educational content"""
    try:
        # Validate content type
        valid_types = [ct.value for ct in ContentType]
        if content_request.content_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid content type. Valid options: {valid_types}")
        
        # Validate difficulty level
        valid_levels = [dl.value for dl in DifficultyLevel]
        if content_request.difficulty_level not in valid_levels:
            raise HTTPException(status_code=400, detail=f"Invalid difficulty level. Valid options: {valid_levels}")
        
        # Convert to enums
        content_type = ContentType(content_request.content_type)
        difficulty_level = DifficultyLevel(content_request.difficulty_level)
        
        # Create educational service
        educational_service = EducationalService(db)
        
        # Create content
        result = educational_service.create_educational_content(
            title=content_request.title,
            content_type=content_type,
            difficulty_level=difficulty_level,
            description=content_request.description,
            content_url=content_request.content_url,
            content_text=content_request.content_text,
            content_duration=content_request.content_duration,
            tags=content_request.tags,
            category=content_request.category,
            author=content_request.author,
            language=content_request.language
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating educational content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content")
async def get_educational_content(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    limit: int = Query(50, description="Maximum number of content to return"),
    db: Session = Depends(get_db)
):
    """Get educational content"""
    try:
        # Convert to enums if provided
        content_type_enum = None
        if content_type:
            valid_types = [ct.value for ct in ContentType]
            if content_type not in valid_types:
                raise HTTPException(status_code=400, detail=f"Invalid content type. Valid options: {valid_types}")
            content_type_enum = ContentType(content_type)
        
        difficulty_level_enum = None
        if difficulty_level:
            valid_levels = [dl.value for dl in DifficultyLevel]
            if difficulty_level not in valid_levels:
                raise HTTPException(status_code=400, detail=f"Invalid difficulty level. Valid options: {valid_levels}")
            difficulty_level_enum = DifficultyLevel(difficulty_level)
        
        educational_service = EducationalService(db)
        content = educational_service.get_educational_content(
            content_type=content_type_enum,
            difficulty_level=difficulty_level_enum,
            limit=limit
        )
        
        return {
            "content": content,
            "total_count": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting educational content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/journal/create")
async def create_trading_journal_entry(
    journal_request: CreateTradingJournalRequest,
    db: Session = Depends(get_db)
):
    """Create trading journal entry"""
    try:
        # Validate entry type
        valid_types = [jt.value for jt in JournalEntryType]
        if journal_request.entry_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid entry type. Valid options: {valid_types}")
        
        # Convert to enum
        entry_type = JournalEntryType(journal_request.entry_type)
        
        educational_service = EducationalService(db)
        result = educational_service.create_trading_journal_entry(
            user_id="default_user",  # This would be from authentication
            title=journal_request.title,
            entry_type=entry_type,
            content=journal_request.content,
            symbol=journal_request.symbol,
            trade_date=journal_request.trade_date,
            entry_price=journal_request.entry_price,
            exit_price=journal_request.exit_price,
            quantity=journal_request.quantity,
            pnl=journal_request.pnl,
            pnl_percent=journal_request.pnl_percent,
            analysis_data=journal_request.analysis_data,
            lessons_learned=journal_request.lessons_learned,
            mistakes_made=journal_request.mistakes_made,
            improvements=journal_request.improvements,
            tags=journal_request.tags
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating trading journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/journal")
async def get_trading_journal_entries(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, description="Maximum number of entries to return"),
    offset: int = Query(0, description="Number of entries to skip"),
    db: Session = Depends(get_db)
):
    """Get trading journal entries"""
    try:
        educational_service = EducationalService(db)
        entries = educational_service.get_trading_journal_entries(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "entries": entries,
            "total_count": len(entries)
        }
        
    except Exception as e:
        logger.error(f"Error getting trading journal entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learning-path/create")
async def create_learning_path(
    path_request: CreateLearningPathRequest,
    db: Session = Depends(get_db)
):
    """Create learning path"""
    try:
        # Validate difficulty level
        valid_levels = [dl.value for dl in DifficultyLevel]
        if path_request.difficulty_level not in valid_levels:
            raise HTTPException(status_code=400, detail=f"Invalid difficulty level. Valid options: {valid_levels}")
        
        # Convert to enum
        difficulty_level = DifficultyLevel(path_request.difficulty_level)
        
        educational_service = EducationalService(db)
        result = educational_service.create_learning_path(
            name=path_request.name,
            description=path_request.description,
            difficulty_level=difficulty_level,
            content_order=path_request.content_order,
            prerequisites=path_request.prerequisites,
            learning_objectives=path_request.learning_objectives,
            estimated_duration=path_request.estimated_duration
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-paths")
async def get_learning_paths(
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    limit: int = Query(50, description="Maximum number of paths to return"),
    db: Session = Depends(get_db)
):
    """Get learning paths"""
    try:
        # Convert to enum if provided
        difficulty_level_enum = None
        if difficulty_level:
            valid_levels = [dl.value for dl in DifficultyLevel]
            if difficulty_level not in valid_levels:
                raise HTTPException(status_code=400, detail=f"Invalid difficulty level. Valid options: {valid_levels}")
            difficulty_level_enum = DifficultyLevel(difficulty_level)
        
        educational_service = EducationalService(db)
        paths = educational_service.get_learning_paths(
            difficulty_level=difficulty_level_enum,
            limit=limit
        )
        
        return {
            "paths": paths,
            "total_count": len(paths)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting learning paths: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/goals/create")
async def create_trading_goal(
    goal_request: CreateTradingGoalRequest,
    db: Session = Depends(get_db)
):
    """Create trading goal"""
    try:
        educational_service = EducationalService(db)
        result = educational_service.create_trading_goal(
            user_id="default_user",  # This would be from authentication
            title=goal_request.title,
            goal_type=goal_request.goal_type,
            target_value=goal_request.target_value,
            unit=goal_request.unit,
            start_date=goal_request.start_date,
            target_date=goal_request.target_date,
            description=goal_request.description
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating trading goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/goals")
async def get_trading_goals(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, description="Maximum number of goals to return"),
    db: Session = Depends(get_db)
):
    """Get trading goals"""
    try:
        educational_service = EducationalService(db)
        goals = educational_service.get_trading_goals(
            user_id=user_id,
            limit=limit
        )
        
        return {
            "goals": goals,
            "total_count": len(goals)
        }
        
    except Exception as e:
        logger.error(f"Error getting trading goals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz/create")
async def create_trading_quiz(
    quiz_request: CreateQuizRequest,
    db: Session = Depends(get_db)
):
    """Create trading quiz"""
    try:
        # Validate difficulty level
        valid_levels = [dl.value for dl in DifficultyLevel]
        if quiz_request.difficulty_level not in valid_levels:
            raise HTTPException(status_code=400, detail=f"Invalid difficulty level. Valid options: {valid_levels}")
        
        # Convert to enum
        difficulty_level = DifficultyLevel(quiz_request.difficulty_level)
        
        educational_service = EducationalService(db)
        result = educational_service.create_trading_quiz(
            title=quiz_request.title,
            description=quiz_request.description,
            difficulty_level=difficulty_level,
            questions=quiz_request.questions,
            time_limit=quiz_request.time_limit,
            passing_score=quiz_request.passing_score
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating trading quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz/submit")
async def submit_quiz_attempt(
    attempt_request: SubmitQuizAttemptRequest,
    db: Session = Depends(get_db)
):
    """Submit quiz attempt"""
    try:
        educational_service = EducationalService(db)
        result = educational_service.submit_quiz_attempt(
            user_id="default_user",  # This would be from authentication
            quiz_id=attempt_request.quiz_id,
            answers=attempt_request.answers,
            time_taken=attempt_request.time_taken
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting quiz attempt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/learning")
async def get_learning_analytics(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """Get learning analytics"""
    try:
        educational_service = EducationalService(db)
        analytics = educational_service.get_learning_analytics(user_id=user_id)
        
        if "error" in analytics:
            raise HTTPException(status_code=400, detail=analytics["error"])
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting learning analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/journal")
async def get_trading_journal_analytics(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """Get trading journal analytics"""
    try:
        educational_service = EducationalService(db)
        analytics = educational_service.get_trading_journal_analytics(user_id=user_id)
        
        if "error" in analytics:
            raise HTTPException(status_code=400, detail=analytics["error"])
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trading journal analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content-types")
async def get_content_types(db: Session = Depends(get_db)):
    """Get available content types"""
    try:
        content_types = []
        for content_type in ContentType:
            content_types.append({
                "type": content_type.value,
                "name": content_type.value.replace('_', ' ').title(),
                "description": f"{content_type.value.replace('_', ' ').title()} content"
            })
        
        return {
            "content_types": content_types,
            "total_count": len(content_types)
        }
        
    except Exception as e:
        logger.error(f"Error getting content types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/difficulty-levels")
async def get_difficulty_levels(db: Session = Depends(get_db)):
    """Get available difficulty levels"""
    try:
        difficulty_levels = []
        for level in DifficultyLevel:
            difficulty_levels.append({
                "level": level.value,
                "name": level.value.replace('_', ' ').title(),
                "description": f"{level.value.replace('_', ' ').title()} level content"
            })
        
        return {
            "difficulty_levels": difficulty_levels,
            "total_count": len(difficulty_levels)
        }
        
    except Exception as e:
        logger.error(f"Error getting difficulty levels: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/journal-entry-types")
async def get_journal_entry_types(db: Session = Depends(get_db)):
    """Get available journal entry types"""
    try:
        entry_types = []
        for entry_type in JournalEntryType:
            entry_types.append({
                "type": entry_type.value,
                "name": entry_type.value.replace('_', ' ').title(),
                "description": f"{entry_type.value.replace('_', ' ').title()} journal entry"
            })
        
        return {
            "entry_types": entry_types,
            "total_count": len(entry_types)
        }
        
    except Exception as e:
        logger.error(f"Error getting journal entry types: {e}")
        raise HTTPException(status_code=500, detail=str(e))
