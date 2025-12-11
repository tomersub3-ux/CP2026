"""
Codeforces API client for Competitive Programming Platform.
Handles fetching user info, submissions, and syncing progress.
"""
import time
import requests
from typing import Optional
from datetime import datetime

# Base URL for Codeforces API
CF_API_BASE = "https://codeforces.com/api"

# Rate limiting: max 5 requests per second
_last_request_time = 0
_min_interval = 0.2  # 200ms between requests


def _rate_limited_request(url: str) -> dict | None:
    """Make a rate-limited request to Codeforces API."""
    global _last_request_time
    
    # Enforce rate limit
    elapsed = time.time() - _last_request_time
    if elapsed < _min_interval:
        time.sleep(_min_interval - elapsed)
    
    try:
        response = requests.get(url, timeout=10)
        _last_request_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK":
                return data.get("result")
        return None
    except Exception as e:
        print(f"CF API error: {e}")
        return None


def get_user_info(handle: str) -> dict | None:
    """
    Get Codeforces user info.
    Returns dict with rating, rank, etc. or None if failed.
    """
    url = f"{CF_API_BASE}/user.info?handles={handle}"
    result = _rate_limited_request(url)
    if result and len(result) > 0:
        return result[0]
    return None


def get_user_submissions(handle: str, count: int = 100) -> list[dict]:
    """
    Get user's recent submissions.
    Returns list of submission dicts.
    """
    url = f"{CF_API_BASE}/user.status?handle={handle}&from=1&count={count}"
    result = _rate_limited_request(url)
    return result if result else []


def get_accepted_problems(handle: str) -> set[tuple[int, str]]:
    """
    Get set of (contest_id, problem_index) for all accepted submissions.
    """
    submissions = get_user_submissions(handle, count=1000)
    accepted = set()
    
    for sub in submissions:
        if sub.get("verdict") == "OK":
            problem = sub.get("problem", {})
            contest_id = problem.get("contestId")
            index = problem.get("index")
            if contest_id and index:
                accepted.add((contest_id, index))
    
    return accepted


def sync_user_progress(user_id: int, cf_handle: str) -> tuple[int, str]:
    """
    Sync user's Codeforces submissions with local problems.
    Returns (count_synced, message).
    """
    from models import get_session, Problem, Submission
    
    if not cf_handle:
        return 0, "No Codeforces handle set."
    
    # Get accepted problems from CF
    accepted = get_accepted_problems(cf_handle)
    if not accepted:
        return 0, "No accepted submissions found or API error."
    
    session = get_session()
    try:
        # Get all CF problems in our database
        cf_problems = session.query(Problem).filter(
            Problem.cf_contest_id.isnot(None),
            Problem.cf_problem_index.isnot(None)
        ).all()
        
        synced = 0
        for problem in cf_problems:
            key = (problem.cf_contest_id, problem.cf_problem_index)
            if key in accepted:
                # Check if already submitted
                existing = session.query(Submission).filter(
                    Submission.user_id == user_id,
                    Submission.problem_id == problem.id
                ).first()
                
                if not existing:
                    submission = Submission(
                        user_id=user_id,
                        problem_id=problem.id,
                        solved_at=datetime.utcnow()
                    )
                    session.add(submission)
                    synced += 1
        
        session.commit()
        return synced, f"Synced {synced} new solved problems!"
    except Exception as e:
        session.rollback()
        return 0, f"Error: {str(e)}"
    finally:
        session.close()


def validate_handle(handle: str) -> tuple[bool, str]:
    """Validate that a Codeforces handle exists."""
    info = get_user_info(handle)
    if info:
        rating = info.get("rating", "Unrated")
        rank = info.get("rank", "unknown")
        return True, f"Found: {handle} (Rating: {rating}, Rank: {rank})"
    return False, "Handle not found on Codeforces."
