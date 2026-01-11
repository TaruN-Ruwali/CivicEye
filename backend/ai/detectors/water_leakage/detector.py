"""
Water Leakage Detection Module

Uses YOLO object detection to identify water leakage in images.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from ultralytics import YOLO
import yaml
import logging

logger = logging.getLogger(__name__)


class WaterLeakageDetector:
    """
    Detector for water leakage in images.
    
    Uses YOLO model for object detection. Configuration is loaded from config.yaml
    if available, otherwise uses default values.
    """
    
    DEFAULT_CONF_THRESHOLD = 0.25
    DEFAULT_IOU_THRESHOLD = 0.45
    
    def __init__(self, base_dir: Path):
        """
        Initialize the water leakage detector.
        
        Args:
            base_dir: Path to the detector directory containing model.pt and config.yaml
        """
        self.base_dir = Path(base_dir)
        self.model_path = self.base_dir / "model.pt"
        self.config_path = self.base_dir / "config.yaml"
        self.model = None
        self.conf_threshold = self.DEFAULT_CONF_THRESHOLD
        self.iou_threshold = self.DEFAULT_IOU_THRESHOLD
        
        # Load configuration
        self._load_config()
        
        # Load model
        if self.model_path.exists():
            try:
                self.model = YOLO(str(self.model_path))
                logger.info(f"WaterLeakageDetector: Model loaded from {self.model_path}")
            except Exception as e:
                logger.error(f"WaterLeakageDetector: Failed to load model: {e}")
        else:
            logger.warning(f"WaterLeakageDetector: Model file not found at {self.model_path}")
    
    def _load_config(self) -> None:
        """Load configuration from config.yaml if it exists."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if config:
                        self.conf_threshold = config.get('conf_threshold', self.DEFAULT_CONF_THRESHOLD)
                        self.iou_threshold = config.get('iou_threshold', self.DEFAULT_IOU_THRESHOLD)
                        logger.info(f"WaterLeakageDetector: Config loaded from {self.config_path}")
            except Exception as e:
                logger.warning(f"WaterLeakageDetector: Failed to load config: {e}, using defaults")
        else:
            logger.debug(f"WaterLeakageDetector: Config file not found at {self.config_path}, using defaults")
    
    def detect(self, image_path: str) -> Dict[str, Any]:
        """
        Detect water leakage in the given image.
        
        Args:
            image_path: Path to the image file to analyze
            
        Returns:
            Dictionary containing detection results:
            {
                "type": "water_leakage",
                "detected": bool,
                "confidence": float (0.0-1.0),
                "boxes": List[List[float]],  # Bounding boxes [x1, y1, x2, y2]
                "label": Optional[str],
                "error": Optional[str]
            }
        """
        if self.model is None:
            return {
                "type": "water_leakage",
                "detected": False,
                "confidence": 0.0,
                "boxes": [],
                "label": None,
                "error": "model missing"
            }
        
        try:
            # Run YOLO prediction with configurable thresholds
            results = self.model.predict(
                source=image_path,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            boxes: List[List[float]] = []
            best_conf = 0.0
            best_label = None
            
            # Process detection results
            # For base YOLO models, look for objects that might indicate water leakage
            water_indicators = ["bottle", "cup", "glass", "water", "liquid", "puddle", "pool"]
            
            for r in results:
                for box in r.boxes:
                    bbox = box.xyxy[0].cpu().numpy().tolist()
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())
                    label = r.names[cls_id].lower()
                    boxes.append(bbox)
                    
                    # Check if detected object might be water-related
                    is_water_related = any(indicator in label for indicator in water_indicators)
                    
                    # For water leakage detection, prioritize water-related objects
                    if is_water_related and conf > best_conf:
                        best_conf = conf
                        best_label = label
                    elif not is_water_related and best_conf == 0.0 and conf > 0.3:
                        # If no water-related objects found, use any high-confidence detection
                        best_conf = conf * 0.5  # Reduce confidence for non-water objects
                        best_label = label
            
            detected = best_conf > 0.0
            
            return {
                "type": "water_leakage",
                "detected": detected,
                "confidence": round(best_conf, 4),
                "boxes": boxes,
                "label": (best_label or None),
                "raw_detections": len(boxes)  # Total number of detections
            }
        except Exception as e:
            logger.error(f"WaterLeakageDetector: Error during detection: {e}", exc_info=True)
            return {
                "type": "water_leakage",
                "detected": False,
                "confidence": 0.0,
                "boxes": [],
                "label": None,
                "error": str(e)
            }

