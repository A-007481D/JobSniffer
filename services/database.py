import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

USE_MOCK_DB = os.getenv("USE_MOCK_DB", "false").lower() == "true"

if USE_MOCK_DB:
    from mock_db import mock_engine as engine
    from mock_db import MockSessionLocal as SessionLocal
    from mock_db import MockBase as Base
    from mock_db import get_mock_db as get_db
else:
    # Use real database
    # Database URL
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/jobsniffer")
    
    engine = create_engine(DATABASE_URL)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create Base class
    Base = declarative_base()
    
    # Dependency to get DB session
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close() 