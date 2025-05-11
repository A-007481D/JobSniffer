# JobSniffer - AI-Powered Job Matching SaaS Platform

JobSniffer is a cutting-edge SaaS platform that revolutionizes the job search process by leveraging AI and machine learning to optimize resumes and match candidates with their ideal job opportunities.

## Features

- **AI Resume Enhancement**: Automated resume parsing, skill extraction, and optimization
- **Smart Job Matching**: AI-driven job listing analysis and semantic matching
- **Job Board Integration**: Automated job scraping from multiple platforms
- **AI-Powered Insights**: Market trend analysis and skill gap analysis

## Tech Stack

- **Backend**: FastAPI, PostgreSQL
- **AI/ML**: LangChain, OpenAI, spaCy
- **Web Scraping**: Playwright, BeautifulSoup
- **Authentication**: JWT
- **Caching**: Redis
- **Message Queue**: RabbitMQ

## Project Structure

```
JobSniffer/
├── services/                  # Microservices
│   ├── user_service/          # User authentication and profile management
│   ├── resume_service/        # Resume parsing and enhancement
│   ├── job_service/           # Job scraping and storage
│   ├── matching_service/      # AI-powered matching engine
│   ├── notification_service/  # Job alerts and updates
│   └── analytics_service/     # Data processing and insights
├── agent/                     # AI agents and scrapers
│   ├── scraper.py             # Job scraping functionality
│   ├── matcher.py             # Job-resume matching functionality
│   ├── ai_module.py           # AI-powered resume enhancement
│   └── notifier.py            # Notification functionality
├── static/                    # Static web files
│   └── index.html             # Simple web interface
├── tests/                     # Test files
├── main.py                    # FastAPI application entry point
├── init_db.py                 # Database initialization script
├── run_app.py                 # Application runner script
└── requirements.txt           # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Docker (optional)

### PostgreSQL Setup

1. **Install PostgreSQL**:
   
   - **Windows**: Download and install from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)
   - **Mac**: `brew install postgresql`
   - **Linux**: `sudo apt install postgresql postgresql-contrib`

2. **Start PostgreSQL Service**:
   
   - **Windows**: It should start automatically after installation
   - **Mac**: `brew services start postgresql`
   - **Linux**: `sudo systemctl start postgresql`

3. **Create a Database**:

   ```bash
   # Access PostgreSQL command line
   psql -U postgres
   
   # Create database
   CREATE DATABASE jobsniffer;
   
   # Quit
   \q
   ```

   Note: If you get authentication errors, you may need to configure `pg_hba.conf` to allow local connections with password or passwordless authentication.

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/jobsniffer.git
   cd jobsniffer
   ```

2. Create and activate a virtual environment:
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Mac/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install core dependencies first:
   ```
   pip install -r core_requirements.txt
   ```

4. Install other dependencies as needed:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://postgres:your_password@localhost/jobsniffer
   JWT_SECRET_KEY=your_jwt_secret_key_here
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   OPENAI_API_KEY=your_openai_api_key_here
   REDIS_URL=redis://localhost:6379/0
   RABBITMQ_URL=amqp://guest:guest@localhost:5672/
   ```

   Replace `your_password` with your PostgreSQL password.

### Running the Application

1. Initialize the database (when running for the first time or after schema changes):
   ```
   python run_app.py --init-db
   ```

2. Start the application:
   ```
   python run_app.py
   ```

3. Access the application:
   - API documentation: `http://localhost:8000/docs`
   - Web UI: `http://localhost:8000/ui`

## API Endpoints

- **User Service**: `/api/users`
  - User registration, authentication, and profile management

- **Resume Service**: `/api/resumes`
  - Resume upload, parsing, and enhancement

- **Job Service**: `/api/jobs`
  - Job search, filtering, and alerts

- **Matching Service**: `/api/matching`
  - Resume-job matching and analysis

- **Notification Service**: `/api/notifications`
  - Notification management

- **Analytics Service**: `/api/analytics`
  - User and market analytics

## Troubleshooting

### Database Connection Issues

1. Check if PostgreSQL is running:
   ```
   # Windows
   pg_isready
   
   # Mac/Linux
   pg_isready -U postgres
   ```

2. Verify database credentials in `.env` file

3. Make sure the database exists:
   ```
   psql -U postgres -c "SELECT 1 FROM pg_database WHERE datname='jobsniffer'"
   ```

### Missing Dependencies

If you experience import errors, install any missing packages:
```
pip install package_name
```

### Frontend Issues

Make sure static files are being served correctly:
```
python -c "import os; print(os.path.exists('static/index.html'))"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 