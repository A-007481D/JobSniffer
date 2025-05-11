import os
import sys
import time
import argparse
import uvicorn
from dotenv import load_dotenv
from sqlalchemy_utils import database_exists

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def run_app(init_db=False, host="0.0.0.0", port=8000, use_mock_db=False):
    """Run JobSniffer application"""
    if use_mock_db:
        print("Using mock database...")
        os.environ["USE_MOCK_DB"] = "true"
        
        # Import and initialize mock database
        from mock_db import init_mock_db
        init_mock_db()
    else:
        os.environ["USE_MOCK_DB"] = "false"
        
        if init_db:
            try:
                print("Initializing database...")
                from init_db import init_db as initialize_database
                initialize_database()
                print("Database initialization completed.")
            except Exception as e:
                print(f"Database initialization failed: {e}")
                print("Continuing with application startup...")
    
    print(f"Starting JobSniffer application on http://{host}:{port}")
    print("Documentation available at:")
    print(f"- API Docs: http://{host}:{port}/docs")
    print(f"- Web UI: http://{host}:{port}/ui")
    
    uvicorn.run("main:app", host=host, port=port, reload=True)

def check_database():
    """Check if database exists and is accessible"""
    from services.database import engine
    
    try:
        # Try to connect to the database
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JobSniffer Application Runner")
    parser.add_argument("--init-db", action="store_true", help="Initialize database before starting")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--mock", action="store_true", help="Use mock database instead of real database")
    args = parser.parse_args()
    
    # Check if database is accessible when not using mock db
    if not args.mock and not check_database():
        print("Database is not accessible. Options:")
        print("1. Make sure PostgreSQL is running and check your database connection settings")
        print("2. Use --mock flag to run with a mock database for demonstration")
        
        # Ask user if they want to continue with mock database
        use_mock = input("Would you like to continue with mock database? (y/n): ").lower() == 'y'
        if use_mock:
            args.mock = True
        else:
            print("Exiting...")
            sys.exit(1)
    
    run_app(init_db=args.init_db, host=args.host, port=args.port, use_mock_db=args.mock) 