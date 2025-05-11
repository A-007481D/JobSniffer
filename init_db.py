import os
import sys
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database import Base, engine
from services.user_service.models.user import UserDB
from services.resume_service.models.resume import ResumeDB, SkillDB
from services.job_service.models.job import JobSourceDB, JobDB, JobAlertDB
from services.matching_service.models.match import MatchDB
from services.notification_service.models.notification import NotificationDB
from services.analytics_service.models.analytics import UserActivityDB, JobMarketTrendDB, UserInsightDB

load_dotenv()

def init_db():
    """Initialize the database"""
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/jobsniffer")

    if not database_exists(db_url):
        create_database(db_url)
        print(f"Created database: {db_url}")
    
    Base.metadata.create_all(bind=engine)
    print("Created database tables")

if __name__ == "__main__":
    init_db() 