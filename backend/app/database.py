"""
Database Configuration and Session Management
Supports both MySQL and in-memory fallback for demo mode
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Base

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://kyc_user:kyc_password123@localhost:3306/ekyc"
)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DB_REQUIRED = os.getenv("DB_REQUIRED", "false").strip().lower() in {"1", "true", "yes", "on"}

# Initialize database engine with connection pooling
engine = None
SessionLocal = None
DB_ENABLED = False

try:
    # Create engine with connection pooling
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True  # Verify connection before using
    )
    
    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    DB_ENABLED = True
    print("✅ MySQL Database connected successfully")
    
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables initialized")
    
except Exception as e:
    print(f"⚠️  MySQL connection failed: {str(e)}")
    if DB_REQUIRED:
        raise
    print("📝 Running in DEMO MODE (in-memory storage)")
    DB_ENABLED = False
    SessionLocal = None

# In-memory storage for demo mode / fallback
MEMORY_STORE = {
    "verifications": [],
    "alerts": [],
    "documents": []
}

def get_db():
    """Dependency for FastAPI to inject database session"""
    if DB_ENABLED and SessionLocal:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None

