from fastapi import APIRouter
from services.user_service.routes.users import router as users_router
from services.user_service.routes.auth import router as auth_router

router = APIRouter()
router.include_router(users_router)
router.include_router(auth_router) 