from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
import cv2
import numpy as np
from app.utils.lut_generator import generate_basic_cube_lut
from app.utils.apply_lut import apply_basic_lut


router = APIRouter()

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"
LUT_DIR = "lut_exports"

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(LUT_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    new_filename = f"{uuid.uuid4().hex}{ext}"
    upload_path = os.path.join(UPLOAD_DIR, new_filename)

    # Save file
    contents = await file.read()
    with open(upload_path, "wb") as f:
        f.write(contents)

    # Load image using OpenCV
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    # Grayscale output
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_path = os.path.join(PROCESSED_DIR, f"gray_{new_filename}")
    cv2.imwrite(processed_path, gray)

    # Dominant Color
    avg_color_bgr = cv2.mean(img)[:3]
    avg_color_rgb = tuple(int(c) for c in avg_color_bgr[::-1])

    # Histograms
    hist_r = (cv2.calcHist([img], [2], None, [256], [0, 256]) / img.size).flatten().tolist()
    hist_g = (cv2.calcHist([img], [1], None, [256], [0, 256]) / img.size).flatten().tolist()
    hist_b = (cv2.calcHist([img], [0], None, [256], [0, 256]) / img.size).flatten().tolist()

    # Generate LUT
    lut_filename = f"{new_filename.split('.')[0]}.cube"
    generate_basic_cube_lut(lut_filename, avg_color_rgb)

    return {
        "original_filename": file.filename,
        "saved_as": new_filename,
        "processed_as": f"gray_{new_filename}",
        "content_type": file.content_type,
        "dominant_color_rgb": avg_color_rgb,
        "histogram": {
            "red": hist_r[:5],
            "green": hist_g[:5],
            "blue": hist_b[:5]
        },
        "generated_lut_file": lut_filename
    }

@router.get("/download-lut/{filename}")
def download_lut(filename: str):
    lut_path = os.path.join(LUT_DIR, filename)

    if not os.path.exists(lut_path):
        raise HTTPException(status_code=404, detail="LUT file not found.")

    return FileResponse(
        lut_path,
        media_type="application/octet-stream",
        filename=filename
    )

@router.post("/apply-lut")
async def apply_lut_to_image(file: UploadFile = File(...), lut_name: str = None):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")
    if not lut_name:
        raise HTTPException(status_code=400, detail="LUT filename is required.")

    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    lut_path = os.path.join("lut_exports", lut_name)
    try:
        processed = apply_basic_lut(img, lut_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="LUT not found.")

    output_name = f"output_{uuid.uuid4().hex}.jpg"
    output_path = os.path.join("outputs", output_name)
    cv2.imwrite(output_path, processed)

    return {
        "output_image": output_name,
        "status": "LUT applied successfully"
    }
