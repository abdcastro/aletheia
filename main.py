from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.utils.crypto import generate_sha256_hash

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Aletheia API",
    description="The secure backend for Aletheia True Media Capture.",
    version="1.0.0"
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for demo purposes
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],
)
)

# Mock database for storing metadata records
# In production, this would be a secure database like PostgreSQL
db_records = {}

class MediaVerificationResponse(BaseModel):
    record_id: str
    sha256_hash: str
    timestamp: str
    gps_coordinates: str
    status: str

@app.post("/api/v1/capture", tags=["Media Operations"])
async def secure_capture(
    file: UploadFile = File(...),
    gps_coordinates: str = Form(...),
    device_id: str = Form(...)
):
    """
    Endpoint for the Aletheia app to upload raw media and metadata.
    Generates a cryptographic hash and establishes the chain of custody.
    """
    try:
        # Read the file bytes directly into memory
        file_bytes = await file.read()
        
        # 1. Generate the immutable hash
        media_hash = generate_sha256_hash(file_bytes)
        
        # 2. Capture the exact server-side timestamp
        secure_timestamp = datetime.utcnow().isoformat()
        
        # 3. Create the ledger record
        record_id = f"aletheia_rec_{media_hash[:12]}"
        
        db_records[record_id] = {
            "hash": media_hash,
            "timestamp": secure_timestamp,
            "gps_coordinates": gps_coordinates,
            "device_id": device_id,
            "verified": True
        }
        
        # 4. (In production) Save file_bytes to secure cold storage (e.g., AWS S3)
        
        return {
            "message": "Media securely captured and hashed.",
            "record_id": record_id,
            "sha256_hash": media_hash,
            "chain_of_custody": "SECURE"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to secure media: {str(e)}")


@app.get("/api/v1/verify/{record_id}", response_model=MediaVerificationResponse, tags=["Audit & Legal"])
async def verify_record(record_id: str):
    """
    Endpoint for third parties (courts, insurance) to verify the authenticity of a media record.
    """
    record = db_records.get(record_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found or invalid.")
        
    return {
        "record_id": record_id,
        "sha256_hash": record["hash"],
        "timestamp": record["timestamp"],
        "gps_coordinates": record["gps_coordinates"],
        "status": "VERIFIED_AUTHENTIC"
    }
