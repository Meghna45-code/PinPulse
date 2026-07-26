from transformers import CLIPModel, CLIPProcessor
import torch
import numpy as np
import logging

logger = logging.getLogger("clip_service")

class CLIPService:
    def __init__(self):
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading CLIP model on {self.device}...")
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            logger.info("CLIP model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            self.model = None
            self.processor = None

    def get_text_embedding(self, text):
        if not text or not self.model:
            return [0.0] * 512
        try:
            inputs = self.processor(text=[text], return_tensors="pt", padding=True, truncation=True).to(self.device)
            with torch.no_grad():
                outputs = self.model.get_text_features(**inputs)
                if not isinstance(outputs, torch.Tensor):
                    outputs = outputs[0]
                outputs = outputs / outputs.norm(p=2, dim=-1, keepdim=True)
            return outputs.cpu().numpy()[0].tolist()
        except Exception as e:
            logger.error(f"Error generating embedding for text '{text}': {e}")
            return [0.0] * 512

# Singleton instance
clip_service = CLIPService()

VIBE_MAPPING = {
    "universal traditionalist": "women's traditional ethnic wear silk saree anarkali suit kurta with traditional embroidery",
    "old money": "women's tailored blazer tailored trousers cashmere sweater minimalist elegant neutral colors linen dress",
    "cottage core": "women's floral midi dress tiered maxi skirt knit cardigan lace trim linen peasant blouse romantic style",
    "alt": "women's edgy streetwear oversized graphic tee cargo pants combat boots distressed denim dark color palette goth grunge",
}

def get_vibe_vector(text):
    text_lower = str(text).lower()
    # Map the vibe to literal visual components if it exists in the dictionary
    if text_lower in VIBE_MAPPING:
        text = VIBE_MAPPING[text_lower]
        
    return clip_service.get_text_embedding(text)
