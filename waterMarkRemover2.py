import cv2
import numpy as np
from pathlib import Path

class WatermarkRemover:
    """
    A class to remove watermarks from images using OpenCV inpainting techniques.
    """
    
    def __init__(self, image_path, output_path=None):
        """
        Initialize the WatermarkRemover.
        
        Args:
            image_path (str): Path to the watermarked image
            output_path (str): Path where the cleaned image will be saved
        """
        self.image_path = image_path
        self.output_path = output_path or self._generate_output_path(image_path)
        self.image = cv2.imread(image_path)
        
        if self.image is None:
            raise ValueError(f"Failed to load image from {image_path}")
        
        self.mask = None
        self.result = None
    
    @staticmethod
    def _generate_output_path(input_path):
        """Generate output path by adding '_cleaned' before file extension."""
        path = Path(input_path)
        return str(path.parent / f"{path.stem}_cleaned{path.suffix}")
    
    def create_mask_by_color(self, lower_color, upper_color):
        """
        Create a mask by detecting pixels within a specific color range.
        
        Args:
            lower_color (tuple): Lower bound of color in BGR format (B, G, R)
            upper_color (tuple): Upper bound of color in BGR format (B, G, R)
        
        Returns:
            np.ndarray: Binary mask
        """
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        self.mask = cv2.inRange(hsv, lower_color, upper_color)
        return self.mask
    
    def create_mask_by_threshold(self, threshold_value=127):
        """
        Create a mask using binary thresholding on grayscale image.
        
        Args:
            threshold_value (int): Threshold value for binary conversion
        
        Returns:
            np.ndarray: Binary mask
        """
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, self.mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        return self.mask
    
    def create_mask_manual(self, mask_array):
        """
        Set a manually created mask.
        
        Args:
            mask_array (np.ndarray): Binary mask array
        """
        if mask_array.shape != self.image.shape[:2]:
            raise ValueError("Mask dimensions do not match image dimensions")
        self.mask = mask_array
        return self.mask
    
    def apply_morphological_operations(self, kernel_size=5, operation='close'):
        """
        Apply morphological operations to refine the mask.
        
        Args:
            kernel_size (int): Size of the morphological kernel
            operation (str): Type of operation - 'open', 'close', 'dilate', 'erode'
        
        Returns:
            np.ndarray: Refined mask
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        if operation == 'open':
            self.mask = cv2.morphologyEx(self.mask, cv2.MORPH_OPEN, kernel)
        elif operation == 'close':
            self.mask = cv2.morphologyEx(self.mask, cv2.MORPH_CLOSE, kernel)
        elif operation == 'dilate':
            self.mask = cv2.dilate(self.mask, kernel, iterations=1)
        elif operation == 'erode':
            self.mask = cv2.erode(self.mask, kernel, iterations=1)
        
        return self.mask
    
    def remove_watermark(self, inpaint_radius=3, method='telea'):
        """
        Remove watermark using inpainting.
        
        Args:
            inpaint_radius (int): Radius of the circular neighborhood around each pixel
            method (str): Inpainting algorithm - 'telea' or 'ns' (Navier-Stokes)
        
        Returns:
            np.ndarray: Inpainted image
        """
        if self.mask is None:
            raise ValueError("Mask not created. Call create_mask_* methods first.")
        
        if method == 'telea':
            self.result = cv2.inpaint(self.image, self.mask, inpaint_radius, cv2.INPAINT_TELEA)
        elif method == 'ns':
            self.result = cv2.inpaint(self.image, self.mask, inpaint_radius, cv2.INPAINT_NS)
        else:
            raise ValueError("Invalid method. Use 'telea' or 'ns'")
        
        return self.result
    
    def save_result(self, path=None):
        """
        Save the cleaned image.
        
        Args:
            path (str): Custom path for saving. Uses default if not provided.
        """
        if self.result is None:
            raise ValueError("No result to save. Run remove_watermark() first.")
        
        save_path = path or self.output_path
        success = cv2.imwrite(save_path, self.result)
        
        if success:
            print(f"✓ Image saved successfully to: {save_path}")
        else:
            raise IOError(f"Failed to save image to {save_path}")
    
    def display_comparison(self, window_title="Watermark Removal Comparison"):
        """
        Display before and after comparison.
        
        Args:
            window_title (str): Title for the display window
        """
        if self.result is None:
            raise ValueError("No result to display. Run remove_watermark() first.")
        
        # Resize for display if image is too large
        h, w = self.image.shape[:2]
        if w > 1200 or h > 800:
            scale = min(1200 / w, 800 / h)
            display_original = cv2.resize(self.image, (int(w * scale), int(h * scale)))
            display_result = cv2.resize(self.result, (int(w * scale), int(h * scale)))
        else:
            display_original = self.image
            display_result = self.result
        
        comparison = np.hstack([display_original, display_result])
        cv2.imshow(window_title, comparison)
        print("Press any key to close the comparison window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


# Example Usage
if __name__ == "__main__":
    # Path to your watermarked image
    image_path = "watermarked_image.jpg"
    
    try:
        # Initialize the remover
        remover = WatermarkRemover(image_path)
        
        # Method 1: Remove watermark by color range (HSV)
        # Adjust these values based on your watermark color
        # For a white/light gray watermark:
        lower_color = np.array([0, 0, 150])      # H, S, V lower bounds
        upper_color = np.array([180, 50, 255])   # H, S, V upper bounds
        
        remover.create_mask_by_color(lower_color, upper_color)
        
        # Refine the mask using morphological operations
        remover.apply_morphological_operations(kernel_size=5, operation='close')
        
        # Apply inpainting to remove the watermark
        remover.remove_watermark(inpaint_radius=5, method='telea')
        
        # Display before and after
        remover.display_comparison()
        
        # Save the result
        remover.save_result()
        
    except Exception as e:
        print(f"Error: {e}")


# Alternative: Quick Function for Simple Cases
def quick_remove_watermark(image_path, output_path=None):
    """
    Quick function to remove watermark with default settings.
    
    Args:
        image_path (str): Path to watermarked image
        output_path (str): Path to save cleaned image
    """
    remover = WatermarkRemover(image_path, output_path)
    
    # Auto-detect watermark using color-based thresholding
    lower_color = np.array([0, 0, 150])
    upper_color = np.array([180, 50, 255])
    
    remover.create_mask_by_color(lower_color, upper_color)
    remover.apply_morphological_operations(kernel_size=5, operation='close')
    remover.remove_watermark(inpaint_radius=5, method='telea')
    remover.save_result()
    
    return remover.result
