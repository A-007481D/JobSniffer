from fastapi import APIRouter
from services.resume_service.routes.resumes import router as resumes_router
from services.resume_service.routes.analysis import router as analysis_router

router = APIRouter()
router.include_router(resumes_router)
router.include_router(analysis_router) 