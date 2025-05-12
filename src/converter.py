from PIL import Image
import pillow_heif
import os
import logging
import rawpy

class ImageConverter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pillow_heif.register_heif_opener()
        self.converted_images = {}
        self.max_size = 4096  # Prevent oversized images

    def convert_image(self, img_path):
        if img_path.lower().endswith(('.jpg', '.jpeg')):
            raise ValueError("File is   already JPG format")
            
        try:
            # RAW file handling
            if img_path.lower().endswith(('.nef', '.cr2', '.arw', '.rw2', '.orf', '.raf')):
                with rawpy.imread(img_path) as raw:
                    rgb_image = raw.postprocess(
                        use_camera_wb=True,
                        no_auto_bright=True,
                        output_bps=16
                    )
                    rgb_image_8bit = (rgb_image / 256).astype('uint8')
                    image = Image.fromarray(rgb_image_8bit)
            else:
                with Image.open(img_path) as img:
                    image = img.convert("RGB") if img.mode != "RGB" else img.copy()

            # # Size optimization
            # if max(image.size) > self.max_size:
            #     image.thumbnail((self.max_size, self.max_size))
                
            filename = os.path.basename(img_path).rsplit(".", 1)[0] + ".jpg"
            self.converted_images[img_path] = (image, filename)
            
        except Exception as e:
            self.logger.error(f"Conversion failed: {str(e)}")
            raise

            raise
    
    
    def save_converted(self, folder):
        for _, (image, filename) in self.converted_images.items():
            try:
                # Save the image with the highest quality and embed the ICC profile if available
                icc_profile = image.info.get("icc_profile")
                image.save(
                    os.path.join(folder, filename),
                    "JPEG",
                    quality=100,  # Maximum quality for JPEG
                    optimize=True,  # Optimize the file size without losing quality
                    progressive=True,  # Enable progressive JPEG for better loading
                    icc_profile=icc_profile  # Embed ICC profile if available
                )
            except Exception as e:
                self.logger.error(f"Error saving {filename}: {str(e)}")
                raise
            
            
    def clear_converted(self):
        self.converted_images.clear()

    def get_comparison_images(self, img_path):
        if img_path not in self.converted_images:
            return Image.open(img_path), None
        return Image.open(img_path), self.converted_images[img_path][0]