import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# Import routers from services
from services.user_service.routes import router as user_router
from services.resume_service.routes import router as resume_router
from services.job_service.routes import router as job_router
from services.matching_service.routes import router as matching_router
from services.notification_service.routes import router as notification_router
from services.analytics_service.routes import router as analytics_router

app = FastAPI(
    title="JobSniffer API",
    description="""
    AI-Powered Job Matching SaaS Platform
    
    JobSniffer is a cutting-edge SaaS platform that revolutionizes the job search process by leveraging AI 
    and machine learning to optimize resumes and match candidates with their ideal job opportunities.
    
    ## Features
    
    * **AI Resume Enhancement**: Automated resume parsing, skill extraction, and optimization
    * **Smart Job Matching**: AI-driven job listing analysis and semantic matching
    * **Job Board Integration**: Automated job scraping from multiple platforms
    * **AI-Powered Insights**: Market trend analysis and skill gap analysis
    """,
    version="1.0.0",
    contact={
        "name": "JobSniffer Support",
        "email": "support@jobsniffer.com",
    },
    license_info={
        "name": "MIT License",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(resume_router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(job_router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(matching_router, prefix="/api/matching", tags=["Matching"])
app.include_router(notification_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", tags=["Root"], summary="Welcome endpoint", description="Returns a welcome message for the JobSniffer API")
async def root():
    return {"message": "Welcome to JobSniffer API", "status": "online"}

@app.get("/health", tags=["Health"], summary="Health check endpoint", description="Returns the health status of the API")
async def health():
    return {"status": "healthy"}

@app.get("/ui", tags=["UI"], summary="Web UI", description="Redirects to the web user interface")
async def ui():
    return RedirectResponse(url="/static/index.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
