"""
Health Device Compatibility & Vitals Data Service
Supports collecting, importing, and monitoring readings from standard health devices
(BP Monitors, Pulse Oximeters, Glucometers, Thermometers).
Enforces Medical Safety Invariants (Rule 8: Vitals monitoring, not automated diagnosis).
"""

import json
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

        # Clinical Range Checks
        if "SpO2" in metric_name or "ऑक्सीजन" in metric_name:
            try:
                num = float(val_clean.replace("%", ""))
                if num < 92:
                    status = "गंभीर (Critical Alert)"
                    alert = "⚠️ ऑक्सीजन का स्तर (SpO2) 92% से कम है। कृपया तुरंत डॉक्टर या 108 एम्बुलेंस से संपर्क करें।"
                elif num < 95:
                    status = "चेतावनी (Low Warning)"
                    alert = "ऑक्सीजन स्तर सामान्य से हल्का कम है। 15 मिनट बाद दोबारा नापें।"
            except Exception:
                pass

        elif "Blood Pressure" in metric_name or "रक्तचाप" in metric_name:
            try:
                parts = val_clean.split("/")
                if len(parts) == 2:
                    sys, dia = float(parts[0]), float(parts[1])
                    if sys >= 140 or dia >= 90:
                        status = "उच्च रक्तचाप (High BP Warning)"
                        alert = "⚠️ रक्तचाप सामान्य (120/80) से अधिक है। आराम करें और डॉक्टर को सूचित करें।"
                    elif sys < 90 or dia < 60:
                        status = "निम्न रक्तचाप (Low BP Warning)"
                        alert = "⚠️ रक्तचाप कम (Low BP) है। ओआरएस या पानी पिएं और डॉक्टर से पूछें।"
            except Exception:
                pass

        elif "Blood Sugar" in metric_name or "शुगर" in metric_name:
            try:
                num = float(val_clean)
                if num > 200:
                    status = "उच्च शुगर (High Sugar Warning)"
                    alert = "रक्त शर्करा 200 mg/dL से अधिक है। मीठा न लें और डॉक्टर से परामर्श करें।"
                elif num < 70:
                    status = "कम शुगर (Low Sugar / Hypo Alert)"
                    alert = "⚠️ शुगर 70 mg/dL से कम है। तुरंत थोड़ा मीठा पानी या ग्लूकोज लें।"
            except Exception:
                pass

        elif "Temperature" in metric_name or "बुखार" in metric_name:
            try:
                num = float(val_clean.replace("°F", "").replace("F", ""))
                if num >= 101.0:
                    status = "तेज बुखार (High Fever)"
                    alert = "⚠️ तेज बुखार (101°F+) है। ठंडे पानी की पट्टी रखें और डॉक्टर की सलाह लें।"
            except Exception:
                pass

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
