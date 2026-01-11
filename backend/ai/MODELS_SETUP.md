# AI Models Setup Guide

## Overview

CivicEye uses YOLO (You Only Look Once) models for detecting:
- **Garbage** - Trash and waste in images
- **Pothole** - Road potholes and damage
- **Water Leakage** - Water leaks and flooding

## Quick Setup

### Option 1: Use Setup Script (Recommended)

Run the automated setup script:

```bash
cd backend/ai
python setup_models.py
```

This will download base YOLO models (YOLOv8n) to each detector folder.

### Option 2: Manual Download

1. **Download base YOLO models** (for testing):
   ```python
   from ultralytics import YOLO
   
   # Download to garbage detector
   model = YOLO('yolov8n.pt')
   model.save('backend/ai/detectors/garbage/model.pt')
   
   # Download to pothole detector
   model = YOLO('yolov8n.pt')
   model.save('backend/ai/detectors/pothole/model.pt')
   
   # Download to water leakage detector
   model = YOLO('yolov8n.pt')
   model.save('backend/ai/detectors/water_leakage/model.pt')
   ```

2. **Or use custom trained models**:
   - Place your custom `.pt` model files in:
     - `backend/ai/detectors/garbage/model.pt`
     - `backend/ai/detectors/pothole/model.pt`
     - `backend/ai/detectors/water_leakage/model.pt`

## Model Requirements

### File Structure
```
backend/ai/detectors/
├── garbage/
│   ├── model.pt          # Required: YOLO model file
│   ├── config.yaml       # Optional: Configuration
│   └── detector.py
├── pothole/
│   ├── model.pt          # Required: YOLO model file
│   ├── config.yaml       # Optional: Configuration
│   └── detector.py
└── water_leakage/
    ├── model.pt          # Required: YOLO model file
    ├── config.yaml       # Optional: Configuration
    └── detector.py
```

### Model Format
- **Format**: PyTorch `.pt` file
- **Type**: Ultralytics YOLO format (YOLOv5, YOLOv8, etc.)
- **Size**: Typically 5-50 MB per model

## Training Custom Models

For production use, you should train custom models on your specific dataset:

### 1. Prepare Dataset
- Collect images of garbage, potholes, and water leakage
- Annotate images (use tools like LabelImg, Roboflow, etc.)
- Format: YOLO format (one `.txt` file per image with bounding boxes)

### 2. Train Models
```python
from ultralytics import YOLO

# Load base model
model = YOLO('yolov8n.pt')

# Train on your dataset
model.train(
    data='path/to/your/dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16
)

# Save trained model
model.save('path/to/save/model.pt')
```

### 3. Deploy Models
Copy your trained models to the detector folders:
```bash
cp trained_garbage_model.pt backend/ai/detectors/garbage/model.pt
cp trained_pothole_model.pt backend/ai/detectors/pothole/model.pt
cp trained_water_model.pt backend/ai/detectors/water_leakage/model.pt
```

## Using Pre-trained Models

### Option A: Ultralytics Hub
1. Visit [Ultralytics Hub](https://hub.ultralytics.com/)
2. Search for models trained on similar datasets
3. Download and place in detector folders

### Option B: Roboflow Universe
1. Visit [Roboflow Universe](https://universe.roboflow.com/)
2. Search for "garbage detection", "pothole detection", etc.
3. Export models in YOLO format
4. Place in detector folders

### Option C: GitHub/Community Models
- Search GitHub for YOLO models trained on similar tasks
- Download `.pt` files
- Place in detector folders

## Configuration

Each detector can have a `config.yaml` file:

```yaml
conf_threshold: 0.25  # Confidence threshold (0.0-1.0)
iou_threshold: 0.45    # IoU threshold for NMS
```

Default values are used if config file is missing.

## Verification

After setting up models, verify they work:

```bash
cd backend/ai
python test_all_detectors.py
```

Or test individual detectors:
```python
from backend.ai.detectors.garbage.detector import GarbageDetector
from pathlib import Path

detector = GarbageDetector(Path("backend/ai/detectors/garbage"))
result = detector.detect("path/to/test/image.jpg")
print(result)
```

## Troubleshooting

### Model Not Found
- **Error**: "Model file not found"
- **Solution**: Run `python setup_models.py` or manually download models

### Low Detection Accuracy
- **Issue**: Base YOLO models may not detect specific objects well
- **Solution**: Train custom models on your dataset

### Out of Memory
- **Issue**: Large models may not fit in memory
- **Solution**: Use smaller models (yolov8n.pt instead of yolov8x.pt)

### Model Loading Errors
- **Error**: "Failed to load model"
- **Solution**: 
  - Verify model file is valid PyTorch format
  - Check file permissions
  - Ensure Ultralytics is installed: `pip install ultralytics`

## Notes

- Base YOLO models (yolov8n.pt) are general-purpose and may not work well for specific tasks
- For production, always use custom-trained models
- Models are automatically loaded when detectors are initialized
- Missing models will show "UNKNOWN" detection results

