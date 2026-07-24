import os
from PIL import Image
import numpy as np

_YOLO_MODEL = None

def get_yolo_model():
    global _YOLO_MODEL
    if _YOLO_MODEL is None:
        try:
            from ultralytics import YOLO
            print("Loading YOLOv8 model for fashion/person bounding-box detection...")
            _YOLO_MODEL = YOLO("yolov8n.pt")
        except Exception as e:
            print(f"Warning: Could not initialize YOLO model ({e}). Using fallback cropper.")
            _YOLO_MODEL = False
    return _YOLO_MODEL

def crop_fashion_item(img_input, margin_pct=0.08):
    """
    YOLO Bounding Box Fashion Cropper.
    Detects person / fashion apparel in input image, crops out YouTube text overlays,
    background logos, and clutter, returning a clean cropped PIL Image for CLIP.
    """
    if isinstance(img_input, str):
        if not os.path.exists(img_input):
            return None
        try:
            img = Image.open(img_input).convert("RGB")
        except Exception as e:
            print(f"Error opening image {img_input}: {e}")
            return None
    else:
        img = img_input.convert("RGB")

    width, height = img.size
    model = get_yolo_model()

    if not model:
        return img

    try:
        # Run YOLO inference
        results = model(img, verbose=False)
        if not results or len(results) == 0:
            return img

        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            return img

        # Filter for person class (class 0 in COCO dataset)
        person_boxes = [box for box in boxes if int(box.cls[0]) == 0]
        
        target_box = None
        if person_boxes:
            # Pick person bounding box with highest confidence
            person_boxes.sort(key=lambda b: float(b.conf[0]), reverse=True)
            target_box = person_boxes[0].xyxy[0].cpu().numpy()
        else:
            # Fallback: Pick box with largest area
            best_area = 0
            for box in boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                area = (xyxy[2] - xyxy[0]) * (xyxy[3] - xyxy[1])
                if area > best_area:
                    best_area = area
                    target_box = xyxy

        if target_box is None:
            return img

        xmin, ymin, xmax, ymax = target_box
        
        # Add margin padding around bounding box
        w_box = xmax - xmin
        h_box = ymax - ymin
        
        pad_w = w_box * margin_pct
        pad_h = h_box * margin_pct
        
        crop_xmin = max(0, int(xmin - pad_w))
        crop_ymin = max(0, int(ymin - pad_h))
        crop_xmax = min(width, int(xmax + pad_w))
        crop_ymax = min(height, int(ymax + pad_h))

        # Perform crop if area is valid (> 15% of original image)
        crop_area = (crop_xmax - crop_xmin) * (crop_ymax - crop_ymin)
        orig_area = width * height
        
        if crop_area > 0.10 * orig_area:
            cropped = img.crop((crop_xmin, crop_ymin, crop_xmax, crop_ymax))
            return cropped

    except Exception as e:
        print(f"YOLO crop error: {e}")

    return img
