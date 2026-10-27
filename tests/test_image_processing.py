"""
Tests for Image Processing Service
"""

import io
from PIL import Image, ImageDraw
from services.image_processing import ImageProcessingService


def test_empty_image_validation():
    valid, msg = ImageProcessingService.validate_file(b"")
    assert valid is False
    assert "खाली" in msg


def test_valid_image_processing():
    # Create simple synthetic test image
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    bytes_data = buf.getvalue()

    valid, msg = ImageProcessingService.validate_file(bytes_data)
    assert valid is True

    loaded_img, load_err = ImageProcessingService.load_and_normalize(bytes_data)
    assert load_err is None
    assert loaded_img.size == (200, 200)

    quality_ok, quality_msg = ImageProcessingService.assess_quality(loaded_img)
    # White image is bright, assess_quality detects brightness > 240
    assert quality_ok is False
    assert "चमकदार या धुंधली" in quality_msg


def test_bright_paper_with_legible_writing_passes_quality_check():
    img = Image.new("RGB", (600, 450), color=(250, 250, 247))
    draw = ImageDraw.Draw(img)
    draw.rectangle((20, 20, 580, 430), outline=(170, 170, 165), width=2)
    for y in (90, 150, 230, 290, 360):
        draw.line((45, y, 440, y), fill=(45, 55, 45), width=3)

    quality_ok, quality_msg = ImageProcessingService.assess_quality(img)

    assert quality_ok is True
    assert quality_msg is None
