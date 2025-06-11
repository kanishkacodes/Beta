from fastapi import APIRouter, File, UploadFile, HTTPException
import os
import uuid
import cv2
import numpy as np

router = APIRouter()

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    # Ensure upload & processed directories exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    new_filename = f"{uuid.uuid4().hex}{ext}"
    upload_path = os.path.join(UPLOAD_DIR, new_filename)

    # Save original uploaded file
    with open(upload_path, "wb") as f:
        contents = await file.read()
        f.write(contents)

    # Convert to grayscale using OpenCV
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    processed_path = os.path.join(PROCESSED_DIR, f"gray_{new_filename}")
    cv2.imwrite(processed_path, gray)

    return {
        "original_filename": file.filename,
        "saved_as": new_filename,
        "processed_as": f"gray_{new_filename}",
        "content_type": file.content_type
    }
