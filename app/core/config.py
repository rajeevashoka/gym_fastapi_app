import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Gym Management System"
    PROJECT_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gym.db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # SMTP/Email settings
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "")
    #print(SMTP_SERVER,SMTP_PORT,SMTP_USERNAME,SMTP_PASSWORD,FROM_EMAIL)
settings = Settings()

# SECRET_KEY = "SUPER_SECRET_KEY"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 120

# DATABASE_URL = "sqlite:///./gym.db"  # change to Postgres/MySQL in production

# SMTP_EMAIL = 'nalanda.softwares@gmail.com'
# SMTP_PASSWORD = 'wckw rezw wubd qlqb'
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
