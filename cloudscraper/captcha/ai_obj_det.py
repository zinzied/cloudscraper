from __future__ import absolute_import

import base64
import io
import math

try:
    from PIL import Image
    # Patch for older Pillow versions just in case
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass

from ..exceptions import (
    CaptchaServiceUnavailable,
    CaptchaAPIError,
    CaptchaTimeout,
    CaptchaParameter
)

from . import Captcha


class captchaSolver(Captcha):
    def __init__(self):
        super(captchaSolver, self).__init__('ai_obj_det')
        self.model = None

    def _init_yolo(self):
        if self.model is None:
            try:
                from ultralytics import YOLO
                # Load a pretrained YOLOv8n model
                # This will download 'yolov8n.pt' to current dir if not present.
                # using 'yolov8n.pt' (nano) for speed.
                self.model = YOLO('yolov8n.pt')
            except ImportError:
                return False
            except Exception as e:
                raise CaptchaServiceUnavailable(f"ai_obj_det: Failed to load YOLO model -> {e}")
        return True

    def getCaptchaAnswer(self, captchaType, url, siteKey, captchaParams):
        """
        Solves image selection captcha (Grid 3x3 or 4x4).
        
        Requires:
        - captchaParams['image']: base64 string of the grid image.
        - captchaParams['label']: the object to find (e.g. 'car', 'bus', 'traffic light').
        
        Optional:
        - captchaParams['grid_rows']: default 3
        - captchaParams['grid_cols']: default 3
        
        Returns:
        - List of cell indices [0, 1, 5] consisting of the target object.
        """
        image_data = captchaParams.get('image')
        target_label = captchaParams.get('label')

        if not image_data:
            raise CaptchaParameter("ai_obj_det: Missing 'image' parameter (Base64 string).")
        
        if not target_label:
            # Maybe default to something or error? 
            # Error is safer.
            raise CaptchaParameter("ai_obj_det: Missing 'label' parameter (target object name).")

        # Decode base64
        if isinstance(image_data, str):
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception:
                raise CaptchaParameter("ai_obj_det: Invalid Base64 image data.")
        else:
            image_bytes = image_data

        if not self._init_yolo():
             raise CaptchaServiceUnavailable(
                "ai_obj_det: 'ultralytics' library not found. "
                "Please install it: pip install ultralytics"
            )

        # Load image for PIL
        try:
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size
        except Exception as e:
            raise CaptchaParameter(f"ai_obj_det: Failed to load image -> {e}")

        # Run inference
        results = self.model(img, verbose=False)  # list of Results objects

        # Parse results
        # We need to filter by class name == target_label
        # YOLOv8 class names map: model.names (dict {0: 'person', 1: 'bicycle', ...})
        
        # Grid settings
        rows = int(captchaParams.get('grid_rows', 3))
        cols = int(captchaParams.get('grid_cols', 3))
        
        cell_w = width / cols
        cell_h = height / rows
        
        found_indices = set()
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Class id
                cls_id = int(box.cls[0])
                cls_name = self.model.names[cls_id]
                
                # Check if it matches target
                # (Simple substring or exact match? 'traffic light' vs 'traffic_light')
                # Let's handle some common variations or exact match
                if target_label.lower() in cls_name.lower() or cls_name.lower() in target_label.lower():
                    # Calculate center
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    
                    # Determine cell
                    c_idx = int(cx // cell_w)
                    r_idx = int(cy // cell_h)
                    
                    # Clamp just in case
                    c_idx = min(c_idx, cols - 1)
                    r_idx = min(r_idx, rows - 1)
                    
                    cell_index = r_idx * cols + c_idx
                    found_indices.add(cell_index)

        return sorted(list(found_indices))

# ------------------------------------------------------------------------------- #

captchaSolver()
