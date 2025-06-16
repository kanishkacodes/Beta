import numpy as np
import os
import cv2

def apply_basic_lut(image_np: np.ndarray, cube_path: str) -> np.ndarray:
    """
    Simulate LUT application using average color adjustment (basic simulation).
    """
    if not os.path.exists(cube_path):
        raise FileNotFoundError("LUT file not found")

    # Parse .cube to simulate tone scale
    r_shift, g_shift, b_shift = 1.0, 1.0, 1.0
    with open(cube_path, "r") as file:
        lines = file.readlines()
        values = [line.strip() for line in lines if line and not line.startswith(("TITLE", "LUT_3D_SIZE", "DOMAIN"))]
        if values:
            r_sum = g_sum = b_sum = 0
            for line in values[:100]:  # only first 100 entries
                r, g, b = map(float, line.split())
                r_sum += r
                g_sum += g
                b_sum += b
            r_shift = r_sum / 100
            g_shift = g_sum / 100
            b_shift = b_sum / 100

    # Apply tone shift
    result = image_np.astype(np.float32)
    result[..., 0] *= b_shift
    result[..., 1] *= g_shift
    result[..., 2] *= r_shift

    return np.clip(result, 0, 255).astype(np.uint8)
