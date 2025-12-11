"""
Database models for Competitive Programming Platform.
Uses SQLAlchemy ORM with SQLite.
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import bcrypt

# Database setup
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE_PATH = os.path.join(DATA_DIR, "cp_platform.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    """User model for authentication and profile."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    cf_handle = Column(String(50), nullable=True)  # Codeforces handle
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submissions = relationship("Submission", back_populates="user")
    
    def set_password(self, password: str):
        """Hash and set password."""
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def check_password(self, password: str) -> bool:
        """Verify password."""
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())


class Problem(Base):
    """Problem model for tracking problems."""
    __tablename__ = "problems"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    problem_url = Column(String(500), nullable=True)
    points = Column(Integer, default=10)  # Admin-defined points
    cf_contest_id = Column(Integer, nullable=True)  # For Codeforces problems
    cf_problem_index = Column(String(5), nullable=True)  # e.g., "A", "B1"
    added_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submissions = relationship("Submission", back_populates="problem")


class Submission(Base):
    """Tracks user problem completions."""
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    solved_at = Column(DateTime, default=datetime.utcnow)
    cf_submission_id = Column(Integer, nullable=True)  # Codeforces submission ID
    
    # Relationships
    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")


def init_db():
    """Initialize database and create Admin user if not exists."""
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        # Check if Admin exists
        admin = session.query(User).filter(User.username == "Admin").first()
        if not admin:
            admin = User(username="Admin", is_admin=True)
            admin.set_password("12345678")
            session.add(admin)
            session.commit()
            print("Created Admin user with default password.")
    finally:
        session.close()


def get_session():
    """Get a new database session."""
    return SessionLocal()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {DATABASE_PATH}")
