"""
Image Processing and Quality Assessment Service
Ensures safe loading, EXIF rotation, and pre-flight quality checks (Feature B).
"""

import io
from typing import Tuple, Optional
from PIL import Image, ImageOps, ImageStat


MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]


class ImageProcessingService:
    """
    Validates, normalizes, and checks image quality for prescription scans.
    """

    @classmethod
    def validate_file(cls, file_bytes: bytes, filename: str = "upload.jpg") -> Tuple[bool, Optional[str]]:
        if not file_bytes:
            return False, "फ़ाइल खाली है (The uploaded file is empty)."
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            return False, "फ़ाइल का आकार 10 MB से अधिक है (File exceeds 10MB limit)."
        return True, None

    @classmethod
    def load_and_normalize(cls, file_bytes: bytes) -> Tuple[Optional[Image.Image], Optional[str]]:
        """
        Loads image, fixes EXIF orientation, and converts to RGB.
        """
        try:
            image = Image.open(io.BytesIO(file_bytes))
            # Automatically apply EXIF orientation tag if present
            image = ImageOps.exif_transpose(image)
            if image.mode != "RGB":
                image = image.convert("RGB")
            return image, None
        except Exception as e:
            return None, f"तस्वीर लोड करने में त्रुटि (Failed to decode image): {str(e)}"

    @classmethod
    def assess_quality(cls, image: Image.Image) -> Tuple[bool, Optional[str]]:
        """
        Heuristic quality check: Warns if image is excessively dark or washed out.
        Does not block extraction, but provides helpful guidance.
        """
        try:
            grayscale = image.convert("L")
            stat = ImageStat.Stat(grayscale)
            mean_brightness = stat.mean[0]  # 0 to 255
            std_contrast = stat.stddev[0]

            if mean_brightness < 40:
                return False, "चेतावनी: तस्वीर बहुत अंधेरी है। कृपया अच्छी रोशनी में दोबारा फोटो लें।"
            if mean_brightness > 250 or (mean_brightness > 240 and std_contrast < 15):
                return False, "चेतावनी: तस्वीर बहुत चमकदार या धुंधली है।"
            if std_contrast < 15:
                return False, "चेतावनी: तस्वीर में लिखावट का अंतर (contrast) बहुत कम है।"

            return True, None
        except Exception:
            return True, None
