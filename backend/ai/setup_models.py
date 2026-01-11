"""
Setup script to download YOLO models for CivicEye detectors.

This script downloads base YOLO models or allows you to specify custom trained models.
For production use, you should train custom models for garbage, pothole, and water leakage detection.
"""
import os
from pathlib import Path
from ultralytics import YOLO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DETECTORS = {
    "garbage": "yolov8n.pt",  # You can replace with custom model URL or path
    "pothole": "yolov8n.pt",  # You can replace with custom model URL or path
    "water_leakage": "yolov8n.pt",  # You can replace with custom model URL or path
}

# Alternative: Use custom trained models (uncomment and add your model URLs)
# DETECTORS = {
#     "garbage": "https://github.com/your-repo/garbage-detector.pt",
#     "pothole": "https://github.com/your-repo/pothole-detector.pt",
#     "water_leakage": "https://github.com/your-repo/water-leakage-detector.pt",
# }


def download_model(detector_name: str, model_source: str) -> bool:
    """
    Download a YOLO model for a detector.
    
    Args:
        detector_name: Name of the detector (garbage, pothole, water_leakage)
        model_source: Model name (e.g., 'yolov8n.pt') or URL to download from
        
    Returns:
        True if successful, False otherwise
    """
    detector_dir = BASE_DIR / "detectors" / detector_name
    model_path = detector_dir / "model.pt"
    
    # Create detector directory if it doesn't exist
    detector_dir.mkdir(parents=True, exist_ok=True)
    
    # If model already exists, skip
    if model_path.exists():
        logger.info(f"✓ Model already exists for {detector_name}: {model_path}")
        return True
    
    try:
        logger.info(f"Downloading model for {detector_name}...")
        logger.info(f"  Source: {model_source}")
        
        # Load model (Ultralytics will auto-download if it's a standard model name)
        model = YOLO(model_source)
        
        # Save to detector directory
        model.save(str(model_path))
        
        logger.info(f"✓ Successfully downloaded model for {detector_name}")
        logger.info(f"  Saved to: {model_path}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to download model for {detector_name}: {e}")
        return False


def setup_all_models():
    """Download all required models."""
    logger.info("=" * 60)
    logger.info("CivicEye AI Model Setup")
    logger.info("=" * 60)
    logger.info("")
    logger.info("This script will download base YOLO models.")
    logger.info("For production, use custom-trained models for better accuracy.")
    logger.info("")
    
    results = {}
    for detector_name, model_source in DETECTORS.items():
        results[detector_name] = download_model(detector_name, model_source)
        logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("Setup Summary:")
    logger.info("=" * 60)
    for detector_name, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        logger.info(f"  {detector_name:20s} {status}")
    
    all_success = all(results.values())
    if all_success:
        logger.info("")
        logger.info("✓ All models downloaded successfully!")
        logger.info("You can now use the AI detection features.")
    else:
        logger.info("")
        logger.warning("⚠ Some models failed to download.")
        logger.warning("Please check the error messages above.")
    
    return all_success


if __name__ == "__main__":
    setup_all_models()

