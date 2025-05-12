from fastapi import APIRouter
from services.matching_service.routes.matches import router as matches_router

router = APIRouter()
router.include_router(matches_router) 