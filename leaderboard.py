"""
Leaderboard calculations for Competitive Programming Platform.
"""
from datetime import datetime, timedelta
from models import get_session, User, Problem, Submission
from sqlalchemy import func


def get_leaderboard(time_filter: str = "all") -> list[dict]:
    """
    Get leaderboard data.
    
    Args:
        time_filter: "all", "monthly", or "weekly"
    
    Returns:
        List of dicts with username, solved_count, total_points, rank
    """
    session = get_session()
    try:
        # Determine date filter
        if time_filter == "weekly":
            start_date = datetime.utcnow() - timedelta(days=7)
        elif time_filter == "monthly":
            start_date = datetime.utcnow() - timedelta(days=30)
        else:
            start_date = None
        
        # Build query
        query = session.query(
            User.id,
            User.username,
            func.count(Submission.id).label("solved_count"),
            func.coalesce(func.sum(Problem.points), 0).label("total_points")
        ).join(
            Submission, User.id == Submission.user_id, isouter=True
        ).join(
            Problem, Submission.problem_id == Problem.id, isouter=True
        )
        
        if start_date:
            query = query.filter(Submission.solved_at >= start_date)
        
        # Group and order
        query = query.group_by(User.id).order_by(
            func.coalesce(func.sum(Problem.points), 0).desc(),
            func.count(Submission.id).desc()
        )
        
        results = query.all()
        
        leaderboard = []
        for rank, row in enumerate(results, 1):
            leaderboard.append({
                "rank": rank,
                "username": row.username,
                "solved_count": row.solved_count or 0,
                "total_points": row.total_points or 0
            })
        
        return leaderboard
    finally:
        session.close()


def get_user_stats(user_id: int) -> dict:
    """Get stats for a specific user."""
    session = get_session()
    try:
        # Get solved count and points
        result = session.query(
            func.count(Submission.id).label("solved_count"),
            func.coalesce(func.sum(Problem.points), 0).label("total_points")
        ).join(
            Problem, Submission.problem_id == Problem.id
        ).filter(
            Submission.user_id == user_id
        ).first()
        
        # Get user's rank
        leaderboard = get_leaderboard("all")
        user_rank = None
        for entry in leaderboard:
            if session.query(User).filter(User.id == user_id).first().username == entry["username"]:
                user_rank = entry["rank"]
                break
        
        return {
            "solved_count": result.solved_count if result else 0,
            "total_points": result.total_points if result else 0,
            "rank": user_rank
        }
    finally:
        session.close()


def get_user_solved_problems(user_id: int) -> list[int]:
    """Get list of problem IDs solved by user."""
    session = get_session()
    try:
        submissions = session.query(Submission.problem_id).filter(
            Submission.user_id == user_id
        ).all()
        return [s.problem_id for s in submissions]
    finally:
        session.close()
