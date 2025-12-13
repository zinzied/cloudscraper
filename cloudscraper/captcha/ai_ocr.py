from __future__ import absolute_import

import base64
import io
import re

try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass

from ..exceptions import (
    CaptchaServiceUnavailable,
    CaptchaAPIError,
    CaptchaTimeout,
    CaptchaParameter,
    CaptchaBadJobID
)

from . import Captcha


class captchaSolver(Captcha):
    def __init__(self):
        super(captchaSolver, self).__init__('ai_ocr')
        self.ddddocr = None
        self.tesseract_cmd = None

    def _init_ddddocr(self):
        if self.ddddocr is None:
            try:
                import ddddocr
                self.ddddocr = ddddocr.DdddOcr()
            except ImportError:
                return False
        return True

    def _init_tesseract(self):
        try:
            import pytesseract
            # Check if tesseract is installed/callable
            # We don't necessarily need to check version, just import
            return True
        except ImportError:
            return False

    def getCaptchaAnswer(self, captchaType, url, siteKey, captchaParams):
        # cloudscraper doesn't standardly pass image bytes for 'siteKey' but we can reuse it
        # or expect it in captchaParams['image'] (base64)
        
        image_data = captchaParams.get('image')
        
        # If siteKey looks like base64, usage might be sending it there
        if not image_data and siteKey and len(siteKey) > 100:
             image_data = siteKey

        if not image_data:
            raise CaptchaParameter("ai_ocr: Missing 'image' parameter (Base64 string).")

        # Decode base64 if it's a string
        if isinstance(image_data, str):
            # Handle data:image/png;base64, prefix
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception:
                raise CaptchaParameter("ai_ocr: Invalid Base64 image data.")
        else:
            image_bytes = image_data


        # Method 1: ddddocr (Preferred)
        result = None
        if self._init_ddddocr():
            try:
                res = self.ddddocr.classification(image_bytes)
                if res:
                    result = res
            except Exception as e:
                # If ddddocr fails, fall through or raise? 
                # Let's try fallback if possible, but ddddocr is usually quite robust for what it supports.
                raise CaptchaAPIError(f"ai_ocr: ddddocr failed -> {e}")

        # Method 2: pytesseract (Fallback)
        if not result and self._init_tesseract():
            try:
                import pytesseract
                # Convert bytes to Image for pytesseract
                image = Image.open(io.BytesIO(image_bytes))
                res = pytesseract.image_to_string(image)
                # Clean result (remove whitespace/newlines)
                result = res.strip()
            except Exception as e:
                raise CaptchaAPIError(f"ai_ocr: pytesseract failed -> {e}")

        if result:
            # Check for Math expressions (e.g., "5 + 3 =", "10 - 2")
            # Cleaning up the result to help regex (remove = and ? at the end)
            clean_res = result.replace('=', '').replace('?', '').strip()
            
            # Simple math regex: Number Operator Number
            match = re.search(r'^(\d+)\s*([+\-*])\s*(\d+)$', clean_res)
            if match:
                try:
                    num1 = int(match.group(1))
                    op = match.group(2)
                    num2 = int(match.group(3))
                    
                    if op == '+':
                        return str(num1 + num2)
                    elif op == '-':
                        return str(num1 - num2)
                    elif op == '*':
                        return str(num1 * num2)
                except Exception:
                    pass
            
            return result

        raise CaptchaServiceUnavailable(
            "ai_ocr: No supported OCR library found. "
            "Please install 'ddddocr' (pip install ddddocr) or 'pytesseract' (pip install pytesseract)."
        )

# ------------------------------------------------------------------------------- #

captchaSolver()
