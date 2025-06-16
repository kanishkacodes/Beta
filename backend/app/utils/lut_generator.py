import os

def generate_basic_cube_lut(filename: str, rgb: tuple, size: int = 33) -> str:
    """
    Generates a basic LUT (.cube) file simulating a tone shift based on dominant RGB color.
    """
    path = os.path.join("lut_exports", filename)

    with open(path, "w") as f:
        f.write("TITLE \"PresetForge Generated LUT\"\n")
        f.write("LUT_3D_SIZE {}\n".format(size))
        f.write("DOMAIN_MIN 0.0 0.0 0.0\n")
        f.write("DOMAIN_MAX 1.0 1.0 1.0\n")

        for b in range(size):
            for g in range(size):
                for r in range(size):
                    # Normalize RGB
                    r_val = r / (size - 1)
                    g_val = g / (size - 1)
                    b_val = b / (size - 1)

                    # Apply very basic tone shift toward dominant color
                    tone_shift = [
                        min(1.0, r_val * (rgb[0] / 255)),
                        min(1.0, g_val * (rgb[1] / 255)),
                        min(1.0, b_val * (rgb[2] / 255))
                    ]
                    f.write("{:.6f} {:.6f} {:.6f}\n".format(*tone_shift))

    return path
