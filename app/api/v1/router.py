from fastapi import APIRouter
from app.api.v1 import auth, gyms, users, state_country , attendance  # Import attendance router

router = APIRouter()

router.include_router(gyms.router, prefix="", tags=["gyms"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="", tags=["users"])
router.include_router(state_country.router, prefix="", tags=["state_country"])
router.include_router(attendance.router, prefix="", tags=["attendance"])  # Add this line


# from fastapi import APIRouter
# from app.api.v1 import auth, gyms, users

# api_router = APIRouter()

# api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
# api_router.include_router(gyms.router, prefix="/gyms", tags=["Gyms"])
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
