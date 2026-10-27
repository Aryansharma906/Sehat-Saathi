"""
Health Device Compatibility & Vitals Data Service
Supports collecting, importing, and monitoring readings from standard health devices
(BP Monitors, Pulse Oximeters, Glucometers, Thermometers).
Enforces Medical Safety Invariants (Rule 8: Vitals monitoring, not automated diagnosis).
"""

import json
import math
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from models.vitals_and_mental_health import DeviceVitalsReading
from services.storage_config import get_data_dir


DEFAULT_VITALS_FILE = get_data_dir() / "device_vitals.json"


class DeviceDataService:
    def __init__(self, filepath: Path = DEFAULT_VITALS_FILE):
        self.filepath = Path(filepath)
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            self._write_raw([])

    def _read_raw(self) -> List[dict]:
        try:
            if not self.filepath.exists():
                return []
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except Exception:
            return []

    def _write_raw(self, data: List[dict]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def record_reading(
        self,
        device_type: str,
        metric_name: str,
        value: str,
        unit: str,
        sync_source: str = "उपकरण से दर्ज (Device Reading)"
    ) -> DeviceVitalsReading:
        """
        Records a vital reading from a health device and checks clinical threshold flags.
        """
        status = "सामान्य (Normal)"
        alert = None

        val_clean = value.strip()
        metric_lower = metric_name.casefold()

        def parse_number(raw: str, label: str) -> float:
            try:
                number = float(raw)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Enter a valid {label} reading.") from exc
            if not math.isfinite(number):
                raise ValueError(f"Enter a finite {label} reading.")
            return number

        # Clinical Range Checks
        if "spo2" in metric_lower or "ऑक्सीजन" in metric_name:
            if unit.strip().casefold() not in {"%", "percent"}:
                raise ValueError("SpO₂ must be recorded as a percentage.")
            num = parse_number(val_clean.replace("%", "").strip(), "SpO₂")
            if not 0 <= num <= 100:
                raise ValueError("SpO₂ must be between 0 and 100%.")
            if num < 92:
                status = "गंभीर (Critical Alert)"
                alert = "⚠️ ऑक्सीजन का स्तर (SpO₂) 92% से कम है। कृपया तुरंत डॉक्टर या 108 एम्बुलेंस से संपर्क करें।"
            elif num < 95:
                status = "चेतावनी (Low Warning)"
                alert = "ऑक्सीजन स्तर सामान्य से हल्का कम है। 15 मिनट बाद दोबारा नापें।"

        elif "blood pressure" in metric_lower or "रक्तचाप" in metric_name:
            if unit.strip().replace(" ", "").casefold() != "mmhg":
                raise ValueError("Blood pressure must be recorded in mmHg.")
            match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*", val_clean)
            if not match:
                raise ValueError("Blood pressure must use systolic/diastolic format, such as 120/80.")
            systolic, diastolic = (float(part) for part in match.groups())
            if not (0 < systolic <= 350 and 0 < diastolic <= 250):
                raise ValueError("Enter a plausible systolic/diastolic blood pressure reading.")
            if systolic >= 140 or diastolic >= 90:
                status = "उच्च रक्तचाप (High BP Warning)"
                alert = "⚠️ रक्तचाप सामान्य (120/80) से अधिक है। आराम करें और डॉक्टर से सलाह लें।"
            elif systolic < 90 or diastolic < 60:
                status = "निम्न रक्तचाप (Low BP Warning)"
                alert = "रक्तचाप कम हो सकता है। यदि आप अस्वस्थ महसूस कर रहे हैं, तो डॉक्टर से सलाह लें।"

        elif "blood sugar" in metric_lower or "शुगर" in metric_name:
            if unit.strip().replace(" ", "").casefold() != "mg/dl":
                raise ValueError("Blood sugar must be recorded in mg/dL.")
            num = parse_number(val_clean, "blood sugar")
            if not 0 < num <= 2000:
                raise ValueError("Blood sugar must be greater than 0 and no more than 2000 mg/dL.")
            if num > 200:
                status = "उच्च शुगर (High Sugar Warning)"
                alert = "रक्त शर्करा की रीडिंग 200 mg/dL से अधिक है। अपने डॉक्टर से सलाह लें।"
            elif num < 70:
                status = "कम शुगर (Low Sugar / Hypo Alert)"
                alert = "रक्त शर्करा की रीडिंग 70 mg/dL से कम है। अपने डॉक्टर की सलाह या स्थानीय आपातकालीन मार्गदर्शन लें।"

        elif "temperature" in metric_lower or "तापमान" in metric_name or "बुखार" in metric_name:
            unit_normalized = unit.strip().replace("°", "").casefold()
            raw_temperature = val_clean.replace("°", "").strip()
            if raw_temperature.casefold().endswith("f") or raw_temperature.casefold().endswith("c"):
                raw_temperature = raw_temperature[:-1].strip()
            num = parse_number(raw_temperature, "temperature")
            if unit_normalized in {"c", "celsius"}:
                temperature_f = num * 9 / 5 + 32
            elif unit_normalized in {"f", "fahrenheit"}:
                temperature_f = num
            else:
                raise ValueError("Temperature unit must be °F or °C.")
            if not 68 <= temperature_f <= 122:
                raise ValueError("Enter a plausible body-temperature reading.")
            if temperature_f >= 101.0:
                status = "तेज बुखार (High Fever)"
                alert = "तापमान अधिक है। आराम करें और डॉक्टर की सलाह लें।"

        elif "pulse" in metric_lower or "नाड़ी" in metric_name:
            if unit.strip().casefold() not in {"bpm", "beats/min", "beats per minute"}:
                raise ValueError("Pulse must be recorded in beats per minute (bpm).")
            num = parse_number(val_clean, "pulse")
            if not 0 < num <= 300:
                raise ValueError("Pulse must be greater than 0 and no more than 300 beats per minute.")
        else:
            # Do not label unsupported measurements normal when no assessment was made.
            status = "Not assessed (unsupported measurement)"

        reading = DeviceVitalsReading(
            device_type=device_type,
            metric_name=metric_name,
            value=val_clean,
            unit=unit,
            sync_source=sync_source,
            status_flag=status,
            alert_message=alert
        )

        current = self.get_all_readings()
        current.insert(0, reading)
        self._write_raw([r.model_dump() for r in current])
        return reading

    def import_device_json_data(self, json_string: str) -> List[DeviceVitalsReading]:
        """
        Device Compatibility Interface: Parses device data export formats (e.g. from Bluetooth companion export).
        """
        imported = []
        try:
            data = json.loads(json_string)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                reading = self.record_reading(
                    device_type=item.get("device_type", "Health Device"),
                    metric_name=item.get("metric_name", "Vital"),
                    value=str(item.get("value", "")),
                    unit=item.get("unit", ""),
                    sync_source="ब्लूटूथ / डिवाइस एक्सपोर्ट (Device Sync)"
                )
                imported.append(reading)
        except Exception:
            pass
        return imported

    def get_all_readings(self) -> List[DeviceVitalsReading]:
        raw = self._read_raw()
        results = []
        for item in raw:
            try:
                results.append(DeviceVitalsReading.model_validate(item))
            except Exception:
                continue
        return results

    def delete_reading(self, reading_id: str) -> bool:
        """Discards a single recorded device vital reading."""
        current = self.get_all_readings()
        initial_len = len(current)
        filtered = [item for item in current if item.id != reading_id]
        if len(filtered) < initial_len:
            self._write_raw([e.model_dump() for e in filtered])
            return True
        return False

    def clear_readings(self) -> None:
        """Discards all recorded device vitals."""
        self._write_raw([])
