from fastapi import APIRouter
from services.job_service.routes.jobs import router as jobs_router
from services.job_service.routes.alerts import router as alerts_router

router = APIRouter()
router.include_router(jobs_router)
router.include_router(alerts_router) 