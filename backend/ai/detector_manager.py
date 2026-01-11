from pathlib import Path
from typing import List, Dict, Any, Tuple
import importlib.util
import logging
import os

logger = logging.getLogger(__name__)

# Absolute path to ai/
AI_DIR = Path(__file__).resolve().parent
DETECTORS_DIR = AI_DIR / "detectors"


def _load_detector(detector_name: str):
    det_dir = DETECTORS_DIR / detector_name
    module_path = det_dir / "detector.py"

    if not module_path.exists():
        logger.error(f"detector.py missing for {detector_name}")
        return None, None

    spec = importlib.util.spec_from_file_location(
        f"{detector_name}_detector",
        str(module_path)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class_name = "".join(p.capitalize() for p in detector_name.split("_")) + "Detector"
    cls = getattr(module, class_name, None)

    if cls is None:
        logger.error(f"Class {class_name} not found in {module_path}")
        return None, None

    return cls(det_dir), class_name


def run_all(
    image_path: str,
    confidence_threshold: float = 0.9
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:

    if not os.path.exists(image_path):
        return [], {
            "detected_type": None,
            "confidence": 0.0,
            "detector_name": None,
            "error": "image not found"
        }

    detector_names = ["garbage", "pothole", "water_leakage"]
    detectors = []

    for name in detector_names:
        inst, cls_name = _load_detector(name)
        if inst:
            detectors.append((inst, cls_name))

    if not detectors:
        return [], {
            "detected_type": None,
            "confidence": 0.0,
            "detector_name": None,
            "error": "no detectors loaded"
        }

    detections: List[Dict[str, Any]] = []
    best = {
        "detected_type": None,
        "confidence": 0.0,
        "detector_name": None
    }

    for detector, class_name in detectors:
        try:
            res = detector.detect(image_path) or {}

            det_type = (
                res.get("type")
                or res.get("label")
                or res.get("class")
            )

            conf = (
                res.get("confidence")
                or res.get("conf")
                or res.get("score")
                or 0.0
            )
            conf = float(conf)

            detected_type = det_type if conf >= confidence_threshold else None

            record = {
                "detected_type": detected_type,
                "confidence": conf,
                "detector_name": class_name,
                "raw": res
            }
            detections.append(record)

            if conf > best["confidence"]:
                best = {
                    "detected_type": detected_type,
                    "confidence": conf,
                    "detector_name": class_name
                }

        except Exception as e:
            detections.append({
                "detected_type": None,
                "confidence": 0.0,
                "detector_name": class_name,
                "raw": {"error": str(e)}
            })

    if all(d["confidence"] <= 0.0 for d in detections):
        best = {
            "detected_type": "unknown",
            "confidence": 0.0,
            "detector_name": None
        }

    return detections, best


def build_normal_output(detections: List[Dict[str, Any]]) -> Dict[str, Any]:
    result = {
        "garbage": False,
        "pothole": False,
        "water_leakage": False,
        "confidence": {}
    }

    for d in detections:
        t = d.get("detected_type")
        c = float(d.get("confidence", 0.0))

        if t in result:
            result[t] = True
            result["confidence"][t] = c

    return result


def run_all_for_api(image_path: str) -> Dict[str, Any]:
    detections, final = run_all(image_path)
    return {
        "detections": detections,
        "final": final,
        "result": build_normal_output(detections)
    }
