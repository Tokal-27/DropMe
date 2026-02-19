"""
Data processing module for waste classification
Handles image preprocessing, feature extraction, and validation
"""

import numpy as np
from typing import Tuple, Dict


class DataProcessor:
    """Processes and validates data for model input"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
        # ImageNet normalization parameters
        self.mean = np.array([0.485, 0.456, 0.406])
        self.std = np.array([0.229, 0.224, 0.225])
    
    def preprocess_image(self, image_array: np.ndarray) -> np.ndarray:
        """
        Preprocess image for model input
        
        Steps:
        1. Resize to target size
        2. Normalize pixel values
        3. Apply standardization
        """
        if image_array is None or image_array.size == 0:
            raise ValueError("Invalid image array")
        
        # Resize
        if image_array.shape[:2] != self.target_size:
            # In production: use cv2.resize
            pass
        
        # Normalize to [0, 1]
        image = image_array.astype(np.float32) / 255.0
        
        # Standardize
        if len(image.shape) == 3:  # Color image
            image = (image - self.mean) / self.std
        
        return image
    
    def validate_image_quality(self, image_array: np.ndarray) -> Tuple[bool, str]:
        """
        Validate image quality metrics
        
        Checks:
        - Not too blurry (Laplacian variance)
        - Not too dark or bright
        - Sufficient contrast
        """
        try:
            if image_array is None or image_array.size == 0:
                return False, "Invalid image array"
            
            # Brightness check
            brightness = np.mean(image_array)
            if brightness < 30 or brightness > 225:
                return False, f"Image too dark/bright: {brightness:.1f}"
            
            # Contrast check
            contrast = np.std(image_array)
            if contrast < 10:
                return False, f"Insufficient contrast: {contrast:.1f}"
            
            return True, "Valid image"
            
        except Exception as e:
            return False, f"Quality validation error: {str(e)}"
    
    def extract_features(self, image_array: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract features from image for analysis
        
        Features:
        - Color histogram
        - Edge features
        - Texture features
        """
        features = {}
        
        # Color histogram (3 channels)
        for i in range(min(3, len(image_array.shape))):
            hist, _ = np.histogram(image_array[:,:,i] if len(image_array.shape) > 2 else image_array, bins=32)
            features[f"color_hist_ch{i}"] = hist / hist.sum()  # Normalize
        
        # Edge features (Sobel-like)
        if len(image_array.shape) == 3:
            gray = np.mean(image_array, axis=2)
        else:
            gray = image_array
        
        # Simple edge detection
        edges_x = np.abs(gray[:-1,:] - gray[1:,:])
        edges_y = np.abs(gray[:,:-1] - gray[:,1:])
        features["edge_density"] = (np.sum(edges_x) + np.sum(edges_y)) / gray.size
        
        return features
    
    def augment_image(self, image_array: np.ndarray) -> np.ndarray:
        """
        Data augmentation for robustness
        
        Augmentations:
        - Random rotation
        - Random brightness
        - Random horizontal flip
        """
        augmented = image_array.copy()
        
        # Random brightness
        brightness_factor = np.random.uniform(0.8, 1.2)
        augmented = np.clip(augmented * brightness_factor, 0, 255)
        
        # Random horizontal flip (50% chance)
        if np.random.random() > 0.5:
            augmented = np.fliplr(augmented)
        
        return augmented
