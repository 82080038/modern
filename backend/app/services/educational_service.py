"""
Educational Content Service untuk Learning System dan Trading Journal
"""
from sqlalchemy.orm import Session
from app.models.educational import (
    EducationalContent, TradingJournal, LearningPath, UserProgress, 
    TradingGoals, TradingAchievements, UserAchievements, TradingQuiz, QuizAttempts,
    ContentType, DifficultyLevel, JournalEntryType
)
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid
import logging
import json

logger = logging.getLogger(__name__)

class EducationalService:
    """Service untuk educational content operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_educational_content(self,
                                 title: str,
                                 content_type: ContentType,
                                 difficulty_level: DifficultyLevel,
                                 description: str = None,
                                 content_url: str = None,
                                 content_text: str = None,
                                 content_duration: int = None,
                                 tags: List[str] = None,
                                 category: str = None,
                                 author: str = None,
                                 language: str = "en") -> Dict:
        """Create educational content"""
        try:
            # Generate unique content ID
            content_id = f"EC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create content
            content = EducationalContent(
                content_id=content_id,
                title=title,
                description=description,
                content_type=content_type,
                difficulty_level=difficulty_level,
                content_url=content_url,
                content_text=content_text,
                content_duration=content_duration,
                tags=tags,
                category=category,
                author=author,
                language=language
            )
            
            self.db.add(content)
            self.db.commit()
            
            return {
                "content_id": content_id,
                "title": title,
                "status": "created",
                "message": "Educational content created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating educational content: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def create_trading_journal_entry(self,
                                   user_id: str,
                                   title: str,
                                   entry_type: JournalEntryType,
                                   content: str,
                                   symbol: str = None,
                                   trade_date: date = None,
                                   entry_price: float = None,
                                   exit_price: float = None,
                                   quantity: int = None,
                                   pnl: float = None,
                                   pnl_percent: float = None,
                                   analysis_data: Dict = None,
                                   lessons_learned: str = None,
                                   mistakes_made: str = None,
                                   improvements: str = None,
                                   tags: List[str] = None) -> Dict:
        """Create trading journal entry"""
        try:
            # Generate unique entry ID
            entry_id = f"TJ_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create journal entry
            entry = TradingJournal(
                entry_id=entry_id,
                title=title,
                entry_type=entry_type,
                content=content,
                symbol=symbol,
                trade_date=trade_date,
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=quantity,
                pnl=pnl,
                pnl_percent=pnl_percent,
                analysis_data=analysis_data,
                lessons_learned=lessons_learned,
                mistakes_made=mistakes_made,
                improvements=improvements,
                tags=tags
            )
            
            self.db.add(entry)
            self.db.commit()
            
            return {
                "entry_id": entry_id,
                "title": title,
                "status": "created",
                "message": "Trading journal entry created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating trading journal entry: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_trading_journal_entries(self, user_id: str = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get trading journal entries"""
        try:
            query = self.db.query(TradingJournal)
            
            if user_id:
                # Filter by user (this would be implemented with user association)
                pass
            
            entries = query.order_by(TradingJournal.created_at.desc()).offset(offset).limit(limit).all()
            
            entries_data = []
            for entry in entries:
                entries_data.append({
                    "entry_id": entry.entry_id,
                    "title": entry.title,
                    "entry_type": entry.entry_type.value,
                    "content": entry.content,
                    "symbol": entry.symbol,
                    "trade_date": entry.trade_date.isoformat() if entry.trade_date else None,
                    "entry_price": entry.entry_price,
                    "exit_price": entry.exit_price,
                    "quantity": entry.quantity,
                    "pnl": entry.pnl,
                    "pnl_percent": entry.pnl_percent,
                    "analysis_data": entry.analysis_data,
                    "lessons_learned": entry.lessons_learned,
                    "mistakes_made": entry.mistakes_made,
                    "improvements": entry.improvements,
                    "tags": entry.tags,
                    "created_at": entry.created_at.isoformat()
                })
            
            return entries_data
            
        except Exception as e:
            logger.error(f"Error getting trading journal entries: {e}")
            return []
    
    def create_learning_path(self,
                           name: str,
                           description: str = None,
                           difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER,
                           content_order: List[str] = None,
                           prerequisites: List[str] = None,
                           learning_objectives: List[str] = None,
                           estimated_duration: int = None) -> Dict:
        """Create learning path"""
        try:
            # Generate unique path ID
            path_id = f"LP_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create learning path
            path = LearningPath(
                path_id=path_id,
                name=name,
                description=description,
                difficulty_level=difficulty_level,
                content_order=content_order,
                prerequisites=prerequisites,
                learning_objectives=learning_objectives,
                estimated_duration=estimated_duration
            )
            
            self.db.add(path)
            self.db.commit()
            
            return {
                "path_id": path_id,
                "name": name,
                "status": "created",
                "message": "Learning path created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating learning path: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_learning_paths(self, difficulty_level: DifficultyLevel = None, limit: int = 50) -> List[Dict]:
        """Get learning paths"""
        try:
            query = self.db.query(LearningPath).filter(LearningPath.is_public == True)
            
            if difficulty_level:
                query = query.filter(LearningPath.difficulty_level == difficulty_level)
            
            paths = query.order_by(LearningPath.created_at.desc()).limit(limit).all()
            
            paths_data = []
            for path in paths:
                paths_data.append({
                    "path_id": path.path_id,
                    "name": path.name,
                    "description": path.description,
                    "difficulty_level": path.difficulty_level.value,
                    "content_order": path.content_order,
                    "prerequisites": path.prerequisites,
                    "learning_objectives": path.learning_objectives,
                    "estimated_duration": path.estimated_duration,
                    "completion_count": path.completion_count,
                    "average_rating": path.average_rating,
                    "is_featured": path.is_featured,
                    "created_at": path.created_at.isoformat()
                })
            
            return paths_data
            
        except Exception as e:
            logger.error(f"Error getting learning paths: {e}")
            return []
    
    def create_trading_goal(self,
                           user_id: str,
                           title: str,
                           goal_type: str,
                           target_value: float,
                           unit: str,
                           start_date: date,
                           target_date: date,
                           description: str = None) -> Dict:
        """Create trading goal"""
        try:
            # Generate unique goal ID
            goal_id = f"TG_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create goal
            goal = TradingGoals(
                goal_id=goal_id,
                user_id=user_id,
                title=title,
                description=description,
                goal_type=goal_type,
                target_value=target_value,
                unit=unit,
                start_date=start_date,
                target_date=target_date
            )
            
            self.db.add(goal)
            self.db.commit()
            
            return {
                "goal_id": goal_id,
                "title": title,
                "status": "created",
                "message": "Trading goal created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating trading goal: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_trading_goals(self, user_id: str = None, limit: int = 50) -> List[Dict]:
        """Get trading goals"""
        try:
            query = self.db.query(TradingGoals)
            
            if user_id:
                query = query.filter(TradingGoals.user_id == user_id)
            
            goals = query.order_by(TradingGoals.created_at.desc()).limit(limit).all()
            
            goals_data = []
            for goal in goals:
                goals_data.append({
                    "goal_id": goal.goal_id,
                    "user_id": goal.user_id,
                    "title": goal.title,
                    "description": goal.description,
                    "goal_type": goal.goal_type,
                    "target_value": goal.target_value,
                    "current_value": goal.current_value,
                    "unit": goal.unit,
                    "start_date": goal.start_date.isoformat(),
                    "target_date": goal.target_date.isoformat(),
                    "is_achieved": goal.is_achieved,
                    "achieved_at": goal.achieved_at.isoformat() if goal.achieved_at else None,
                    "progress_percent": (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0,
                    "created_at": goal.created_at.isoformat()
                })
            
            return goals_data
            
        except Exception as e:
            logger.error(f"Error getting trading goals: {e}")
            return []
    
    def create_trading_quiz(self,
                           title: str,
                           description: str = None,
                           difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER,
                           questions: List[Dict] = None,
                           time_limit: int = None,
                           passing_score: float = 70.0) -> Dict:
        """Create trading quiz"""
        try:
            # Generate unique quiz ID
            quiz_id = f"TQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create quiz
            quiz = TradingQuiz(
                quiz_id=quiz_id,
                title=title,
                description=description,
                difficulty_level=difficulty_level,
                questions=questions,
                time_limit=time_limit,
                passing_score=passing_score
            )
            
            self.db.add(quiz)
            self.db.commit()
            
            return {
                "quiz_id": quiz_id,
                "title": title,
                "status": "created",
                "message": "Trading quiz created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating trading quiz: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def submit_quiz_attempt(self,
                           user_id: str,
                           quiz_id: str,
                           answers: List[Dict],
                           time_taken: int = None) -> Dict:
        """Submit quiz attempt"""
        try:
            # Get quiz
            quiz = self.db.query(TradingQuiz).filter(TradingQuiz.quiz_id == quiz_id).first()
            if not quiz:
                return {"error": "Quiz not found"}
            
            # Calculate score
            correct_answers = 0
            total_questions = len(quiz.questions) if quiz.questions else 0
            
            for i, answer in enumerate(answers):
                if i < total_questions:
                    question = quiz.questions[i]
                    if answer.get('answer') == question.get('correct_answer'):
                        correct_answers += 1
            
            score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            is_passed = score >= quiz.passing_score
            
            # Generate unique attempt ID
            attempt_id = f"QA_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create attempt
            attempt = QuizAttempts(
                attempt_id=attempt_id,
                user_id=user_id,
                quiz_id=quiz_id,
                score=score,
                total_questions=total_questions,
                correct_answers=correct_answers,
                time_taken=time_taken,
                answers=answers,
                is_passed=is_passed,
                started_at=datetime.now() - timedelta(seconds=time_taken) if time_taken else datetime.now(),
                completed_at=datetime.now()
            )
            
            self.db.add(attempt)
            
            # Update quiz statistics
            quiz.attempt_count += 1
            quiz.average_score = ((quiz.average_score * (quiz.attempt_count - 1)) + score) / quiz.attempt_count
            
            self.db.commit()
            
            return {
                "attempt_id": attempt_id,
                "score": score,
                "is_passed": is_passed,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "time_taken": time_taken,
                "message": "Quiz attempt submitted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error submitting quiz attempt: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_educational_content(self, content_type: ContentType = None, difficulty_level: DifficultyLevel = None, limit: int = 50) -> List[Dict]:
        """Get educational content"""
        try:
            query = self.db.query(EducationalContent).filter(EducationalContent.is_public == True)
            
            if content_type:
                query = query.filter(EducationalContent.content_type == content_type)
            
            if difficulty_level:
                query = query.filter(EducationalContent.difficulty_level == difficulty_level)
            
            content = query.order_by(EducationalContent.created_at.desc()).limit(limit).all()
            
            content_data = []
            for item in content:
                content_data.append({
                    "content_id": item.content_id,
                    "title": item.title,
                    "description": item.description,
                    "content_type": item.content_type.value,
                    "difficulty_level": item.difficulty_level.value,
                    "content_url": item.content_url,
                    "content_duration": item.content_duration,
                    "tags": item.tags,
                    "category": item.category,
                    "author": item.author,
                    "language": item.language,
                    "view_count": item.view_count,
                    "like_count": item.like_count,
                    "rating": item.rating,
                    "rating_count": item.rating_count,
                    "is_featured": item.is_featured,
                    "is_premium": item.is_premium,
                    "created_at": item.created_at.isoformat()
                })
            
            return content_data
            
        except Exception as e:
            logger.error(f"Error getting educational content: {e}")
            return []
    
    def get_learning_analytics(self, user_id: str = None) -> Dict:
        """Get learning analytics"""
        try:
            # This would calculate learning analytics in production
            analytics = {
                "total_content_viewed": 50,
                "total_learning_time": 1200,  # minutes
                "completed_learning_paths": 3,
                "average_quiz_score": 85.5,
                "trading_journal_entries": 25,
                "goals_achieved": 5,
                "total_goals": 8,
                "achievements_earned": 12,
                "learning_streak": 15,  # days
                "favorite_categories": ["Technical Analysis", "Risk Management", "Psychology"],
                "learning_progress": {
                    "beginner": 100,
                    "intermediate": 75,
                    "advanced": 25,
                    "expert": 5
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting learning analytics: {e}")
            return {"error": str(e)}
    
    def get_trading_journal_analytics(self, user_id: str = None) -> Dict:
        """Get trading journal analytics"""
        try:
            # This would calculate journal analytics in production
            analytics = {
                "total_entries": 25,
                "trade_entries": 15,
                "analysis_entries": 8,
                "reflection_entries": 2,
                "total_pnl": 2500.0,
                "win_rate": 0.65,
                "average_trade_duration": 5,  # days
                "most_traded_symbols": ["BBCA", "BBRI", "BMRI"],
                "common_mistakes": ["Overtrading", "Emotional decisions", "Poor risk management"],
                "improvements_made": ["Better entry timing", "Improved risk management", "Better exit strategy"],
                "monthly_entries": {
                    "2024-01": 8,
                    "2024-02": 12,
                    "2024-03": 5
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting trading journal analytics: {e}")
            return {"error": str(e)}
