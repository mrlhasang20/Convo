from PIL import Image
import pillow_heif
import os
import logging

class ImageConverter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pillow_heif.register_heif_opener()
        self.converted_images = {}  # {original_path: (converted_image, filename)}

    def convert_image(self, img_path):
        try:
            # Open the image and ensure it retains its original dimensions
            with Image.open(img_path) as image:
                original_size = image.size  # Get the original dimensions
                converted_image = image.convert("RGB")  # Convert to RGB format
                
                # Verify the dimensions are preserved
                if converted_image.size != original_size:
                    self.logger.warning(f"Image dimensions changed for {img_path}. Restoring original size.")
                    converted_image = converted_image.resize(original_size, Image.Resampling.LANCZOS)
                
                # Generate the filename for the converted image
                filename = os.path.basename(img_path).rsplit(".", 1)[0] + ".jpg"
                self.converted_images[img_path] = (converted_image, filename)
        except Exception as e:
            self.logger.error(f"Error converting {img_path}: {str(e)}")
            raise

    def save_converted(self, folder):
        for _, (image, filename) in self.converted_images.items():
            try:
                image.save(os.path.join(folder, filename), "JPEG", quality=100)
            except Exception as e:
                self.logger.error(f"Error saving {filename}: {str(e)}")
                raise

    def clear_converted(self):
        self.converted_images.clear()

    def get_comparison_images(self, img_path):
        if img_path not in self.converted_images:
            return Image.open(img_path), None
        return Image.open(img_path), self.converted_images[img_path][0]