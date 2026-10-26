"""
Generate Synthetic Prescription Images for Offline/Live Demos
Privacy by design: 100% synthetic fictitious data.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def generate_sample_images():
    out_dir = Path("data/sample_prescriptions")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Clean Sample
    img_clean = Image.new("RGB", (600, 450), color=(250, 250, 245))
    draw = ImageDraw.Draw(img_clean)
    draw.rectangle([(20, 20), (580, 430)], outline=(180, 180, 180), width=2)
    draw.text((40, 40), "COMMUNITY HEALTH CENTRE (SYNTHETIC SAMPLE)", fill=(50, 50, 50))
    draw.text((40, 70), "Patient: Sunita Devi | Date: 2026-10-26", fill=(80, 80, 80))
    draw.line([(40, 100), (560, 100)], fill=(200, 200, 200), width=1)
    draw.text((40, 120), "Rx (Prescription):", fill=(20, 80, 20))
    draw.text((60, 160), "1. Tab. Pan-D  (40mg) - 1 OD empty stomach x 5 days", fill=(20, 20, 20))
    draw.text((60, 210), "2. Tab. Dolo-650 mg - 1 SOS (fever) after food x 3 days", fill=(20, 20, 20))
    draw.text((40, 360), "Dr. A. Sharma (MBBS) - Reg No: 98765", fill=(100, 100, 100))
    img_clean.save(out_dir / "clean_sample_prescription.jpg")

    # 2. Ambiguous Sample
    img_ambig = Image.new("RGB", (600, 450), color=(245, 245, 240))
    draw2 = ImageDraw.Draw(img_ambig)
    draw2.rectangle([(20, 20), (580, 430)], outline=(180, 180, 180), width=2)
    draw2.text((40, 40), "PRIMARY HEALTH POST (SYNTHETIC AMBIGUOUS)", fill=(50, 50, 50))
    draw2.text((40, 70), "Patient: Ramesh Kumar | Date: 2026-10-26", fill=(80, 80, 80))
    draw2.line([(40, 100), (560, 100)], fill=(200, 200, 200), width=1)
    draw2.text((40, 120), "Rx:", fill=(20, 80, 20))
    draw2.text((60, 160), "1. Tab Dolo 650 - 1 TDS pc x 3d", fill=(20, 20, 20))
    draw2.text((60, 210), "2. Cap Amox... [faded/unclear dose] - 1 BD pc", fill=(120, 60, 60))
    draw2.text((40, 360), "Dr. Clinic - Faded Signature", fill=(120, 120, 120))
    img_ambig.save(out_dir / "ambiguous_sample_prescription.jpg")


if __name__ == "__main__":
    generate_sample_images()
