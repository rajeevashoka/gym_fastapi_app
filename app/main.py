from fastapi import FastAPI, Request , Depends , HTTPException , status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from app.db.database import engine, Base
from app.api.v1.router import router as api_router
from app.core.config import settings


# Import all models
from app.db.models import StateCountry, Pincode, Gym, User, Shift, Attendance

# Import the init_shifts function
from app.db.init_data import init_shifts

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# Configure templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Startup event - runs when application starts
@app.on_event("startup")
def on_startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize default shifts using your existing function
    init_shifts()

# Your existing routes remain the same
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/verify-otp", response_class=HTMLResponse)
async def verify_otp_page(request: Request):
    return templates.TemplateResponse("verify_otp.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

#---------
# Add this route to your main.py
from app.db.database import get_db
from app.core.security import get_current_user
from sqlalchemy.orm import Session
from app.db import models, schemas
import datetime

@app.get("/attendance-dashboard", response_class=HTMLResponse)
async def attendance_dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if user has permission
    if not current_user.is_owner and not current_user.is_trainer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and trainers can access attendance dashboard"
        )
    
    return templates.TemplateResponse("attendance_dashboard.html", {
        "request": request,
        "today": datetime.datetime.now().date().isoformat()
    })
#---------

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# import os
# from app.db.database import engine, Base
# from app.api.v1.router import router as api_router
# from app.core.config import settings

# # Import all models to ensure they are registered with Base
# from app.db.models import StateCountry, Pincode, Gym, User

# # Create database tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI(
#     title=settings.PROJECT_NAME,
#     version=settings.PROJECT_VERSION
# )

# # Configure templates directory
# templates = Jinja2Templates(directory="templates")

# # Serve static files (CSS, JS, images)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Include API router
# app.include_router(api_router, prefix="/api/v1")

# # Frontend routes
# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# @app.get("/register", response_class=HTMLResponse)
# async def register_page(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})

# @app.get("/verify-otp", response_class=HTMLResponse)
# async def verify_otp_page(request: Request):
#     return templates.TemplateResponse("verify_otp.html", {"request": request})

# @app.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# @app.get("/dashboard", response_class=HTMLResponse)
# async def dashboard_page(request: Request):
#     # You can add authentication check here later
#     return templates.TemplateResponse("dashboard.html", {"request": request})

# @app.get("/health")
# def health_check():
#     return {"status": "healthy", "database": "connected"}

# # For debugging
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)