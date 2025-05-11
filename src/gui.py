import os
import threading
import time
from queue import Queue
from tkinter import filedialog, Toplevel, messagebox
import customtkinter as ctk
from PIL import Image
from src.converter import ImageConverter
from src.utils import validate_path, save_config
import logging
import rawpy
import logging
import sys

# Animation constants
LOADING_ANIMATION = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
MAX_THREADS = 4  # Optimal for most CPUs

class ImageConverterGUI(ctk.CTk):
    def __init__(self, config):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.converter = ImageConverter()
        self.uploaded_images = []
        self.title("Convo-Local v2")
        self.geometry("1300x750")
        self.minsize(1000, 600)
        
        # Thread management
        self.task_queue = Queue()
        self.active_threads = 0
        self.current_animation = 0
        self.conversion_running = False

        self.configure_gui()
        self.create_widgets()
        self.after(100, self.process_queue)
        
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler("image_converter.log", encoding="utf-8"),
                logging.StreamHandler(sys.stdout)  # Ensure stdout supports Unicode
            ]
        )

    def configure_gui(self):
        ctk.set_appearance_mode("System")
        theme_path = os.path.join(os.path.dirname(__file__), "assets", "theme.json")
        if os.path.exists(theme_path):
            ctk.set_default_color_theme(theme_path)
        else:
            ctk.set_default_color_theme("green")
            
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.update_status(f"Theme set to {new_mode}", "#9b59b6")

    def create_widgets(self):
        # Left panel
        self.left_panel = ctk.CTkFrame(self, width=260, corner_radius=15)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)

        # Right panel
        self.right_panel = ctk.CTkFrame(self, corner_radius=15)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.path_label = ctk.CTkLabel(self.left_panel,text=f"Default: {self.config.get('default_save_folder', 'Not Set')}",wraplength=240,
            font=ctk.CTkFont(size=10, weight="normal"),
            text_color="#7f8c8d"
        )
        self.path_label.pack(pady=(5, 10), fill="x")

        # Control buttons
        control_buttons = [
            ("🌓 Toggle Theme", self.toggle_theme, "#9b59b6"),
            ("📤 Upload Images", self.upload_images, "#2ecc71"),
            ("🗑️ Clear All", self.clear_all, "#e74c3c"),
            ("⚡ Convert All", self.start_conversion, "#3498db"),
            ("💾 Save Converted", self.save_converted_images, "#f1c40f"),
            ("📁 Set Save Folder", self.set_save_folder, "#2c3e50")
        ]

        for text, command, color in control_buttons:
            btn = ctk.CTkButton(
                self.left_panel,
                text=text,
                command=command,
                fg_color=color,
                hover_color=self.darken_color(color),
                corner_radius=8
            )
            btn.pack(pady=5, fill="x", padx=5)

        # Progress and status
        self.progress = ctk.CTkProgressBar(self.left_panel, height=10)
        self.progress.set(0)
        self.progress.pack(pady=(15, 5), fill="x", padx=5)

        self.status_label = ctk.CTkLabel(
            self.left_panel, 
            text="Ready",
            wraplength=240,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.pack(pady=(5, 10), fill="x")

        # Thumbnail tabs
        self.thumb_tabs = ctk.CTkTabview(self.right_panel)
        self.thumb_tabs.pack(fill="both", expand=True, padx=10, pady=10)
        # self.pending_tab = self.thumb_tabs.add("🟡 Pending")
        # self.converted_tab = self.thumb_tabs.add("✅ Converted")
        
        # Scrollable pending tab
        self.pending_tab = ScrollableFrame(self.thumb_tabs.add("🟡 Pending"))
        self.pending_tab.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollable converted tab
        self.converted_tab = ScrollableFrame(self.thumb_tabs.add("✅ Converted"))
        self.converted_tab.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid for thumbnails
        for col in (0, 1, 2):
            self.pending_tab.grid_columnconfigure(col, weight=1)
            self.converted_tab.grid_columnconfigure(col, weight=1)

    def darken_color(self, hex_color, factor=0.8):
        """Generate darker color for hover effects"""
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        darker = tuple(max(0, int(c * factor)) for c in rgb)
        return f'#{darker[0]:02x}{darker[1]:02x}{darker[2]:02x}'

    def update_status(self, message, color="white"):
        self.current_animation = (self.current_animation + 1) % len(LOADING_ANIMATION)
        self.status_label.configure(
            text=f"{LOADING_ANIMATION[self.current_animation]} {message}",
            text_color=color
        )
        self.update_idletasks()

    def process_queue(self):
        if not self.task_queue.empty() and self.active_threads < MAX_THREADS:
            img_path = self.task_queue.get()
            self.active_threads += 1
            threading.Thread(target=self.process_image, args=(img_path,)).start()
        self.after(100, self.process_queue)

    def upload_images(self):
        paths = filedialog.askopenfilenames(filetypes=[
            ("All Images", "*.jpg *.jpeg *.png *.heic *.nef *.cr2 *.arw *.rw2 *.orf *.raf")
        ])
        
        new_files = [p for p in paths if p not in self.uploaded_images]
        self.uploaded_images.extend(new_files)
        self.files_to_convert = new_files
        
        for path in new_files:
            self.add_thumbnail(path, self.pending_tab)
        
        self.update_status(f"Added {len(new_files)} images", "#2ecc71")

    def add_thumbnail(self, img_path, parent, is_converted=False):
        frame = ctk.CTkFrame(parent, corner_radius=10, border_width=2)
        frame.grid(
            row=len(parent.winfo_children()) // 3,
            column=len(parent.winfo_children()) % 3,
            padx=10, pady=10, sticky="nsew"
        )

        try:
            # Thumbnail generation
            img = Image.open(img_path)
            img.thumbnail((150, 150))
            tk_img = ctk.CTkImage(light_image=img, size=img.size)
            
            text_color = "#000000" if ctk.get_appearance_mode() == "Light" else "#FFFFFF"

            # Thumbnail button
            btn = ctk.CTkButton(
                frame, 
                image=tk_img, 
                text=os.path.basename(img_path),
                compound="top",
                command=lambda p=img_path: self.open_full_image(p),
                fg_color="transparent",
                hover_color="#f0f0f0" if ctk.get_appearance_mode() == "Light" else "#34495e",
                text_color=text_color
            )
            btn.pack(pady=5, padx=5)
            
            # "Compare" button only for converted images
            if is_converted:
                ctk.CTkButton(
                    frame, 
                    text="Compare", 
                    command=lambda p=img_path: self.compare_images(p),
                    width=80
                ).pack(pady=(0, 5))

        except Exception as e:
            self.logger.error(f"Thumbnail error: {str(e)}")
            self.update_status(f"Error: {os.path.basename(img_path)}", "red")

    def process_image(self, img_path):
        try:
            # Skip JPG files
            if img_path.lower().endswith(('.jpg', '.jpeg')):
                self.after(0, self.update_status, f"Already in JPG format: {os.path.basename(img_path)}", "#f1c40f")
                return

            # Conversion logic
            self.converter.convert_image(img_path)
            self.after(0, self.move_to_converted, img_path)
            
        except Exception as e:
            self.logger.error(f"Conversion error: {str(e)}")
            self.after(0, self.update_status, f"Error: {os.path.basename(img_path)}", "red")
        finally:
            self.active_threads -= 1

    def move_to_converted(self, img_path):
        # Remove from pending tab
        for child in self.pending_tab.winfo_children():
            if img_path in child.winfo_children()[0].cget("text"):
                child.destroy()
                break

        # Add to converted tab with the "Compare" button
        self.add_thumbnail(img_path, self.converted_tab, is_converted=True)

        # Update progress
        converted = len(self.converter.converted_images)
        total = len(self.uploaded_images)
        self.progress.set(converted / total)

        if converted == total:
            self.update_status("Conversion complete!", "#2ecc71")

    def handle_jpg(self, img_path):
        self.converter.converted_images[img_path] = (Image.open(img_path), os.path.basename(img_path))
        self.move_to_converted(img_path)
        self.update_status(f"Skipped JPG: {os.path.basename(img_path)}", "#f1c40f")

    def clear_all(self):
        self.uploaded_images.clear()
        self.converter.clear_converted()
        
        for child in self.pending_tab.winfo_children():
            child.destroy()
            
        for child in self.converted_tab.winfo_children():
            child.destroy()
            
        self.progress.set(0)
        self.update_status("Cleared all files", "#2ecc71")

            
    def open_full_image(self, img_path):
        try:
            # Open the image
            img = Image.open(img_path)
            w, h = img.size

            # Get the screen dimensions
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()

            # Set a maximum size for the popup window (90% of the screen size)
            max_width = int(screen_width * 0.9)
            max_height = int(screen_height * 0.9)

            # Scale the image down if it exceeds the maximum size
            if w > max_width or h > max_height:
                scale_factor = min(max_width / w, max_height / h)
                new_width = int(w * scale_factor)
                new_height = int(h * scale_factor)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                w, h = img.size  # Update dimensions after resizing

            # Create the popup window
            win = Toplevel(self)
            win.title("🖼️ Full-Size Image")

            # Center the popup window on the screen
            x_offset = (screen_width - w) // 2
            y_offset = (screen_height - h) // 2
            win.geometry(f"{w}x{h}+{x_offset}+{y_offset}")
            win.resizable(False, False)

            # Create a CTkImage for display
            tk_img = ctk.CTkImage(light_image=img, size=(w, h))

            # Display the image in the popup
            label = ctk.CTkLabel(win, image=tk_img, text="", anchor="center")
            label.image = tk_img  # Keep a reference to avoid garbage collection
            label.pack(expand=True, padx=10, pady=10)
            
            # Create theme-safe window
            # win = ctk.CTkToplevel(self)
            # win.transient(self)
            
            # Use system background color
            # bg_color = "#FFFFFF" if ctk.get_appearance_mode() == "Light" else "#2B2B2B"
            
            # canvas = ctk.CTkCanvas(
            #     win, 
            #     width=w, 
            #     height=h, 
            #     bg=bg_color,
            #     highlightthickness=0
            # )
        except Exception as e:
            self.logger.error(f"Error opening full image {img_path}: {str(e)}")
            self.status_label.configure(text="Error opening image", text_color="red")




    def start_conversion(self):
        if not self.uploaded_images:
            self.status_label.configure(text="Upload images first", text_color="red")
            return

        self.conversion_running = True
        threading.Thread(target=self.convert_images).start()

    def convert_images(self):
        total = len(self.files_to_convert)
        for idx, img_path in enumerate(self.files_to_convert):
            try:
                self.process_image(img_path)
                self.progress.set((idx + 1) / total)
            except Exception as e:
                self.logger.error(f"Error converting {img_path}: {str(e)}")
        self.files_to_convert = []  # Clear the list after conversion
        self.conversion_running = False
        self.status_label.configure(text=f"Converted {len(self.converter.converted_images)} images", text_color="green")

    def save_converted_images(self):
        if not self.converter.converted_images:
            self.status_label.configure(text="No converted images to save", text_color="red")
            return
        folder = self.config.get("default_save_folder") or filedialog.askdirectory()
        if not folder:
            return
        try:
            for img_path, (image, filename) in self.converter.converted_images.items():
                save_path = os.path.join(folder, filename)
                image.save(save_path, "JPEG", quality=100, optimize=True, progressive=True)
            self.status_label.configure(text=f"Saved all images to {folder}", text_color="green")
        except Exception as e:
            self.logger.error(f"Error saving images: {str(e)}")
            self.status_label.configure(text="Error saving images", text_color="red")

    def set_save_folder(self):
        folder = filedialog.askdirectory()
        if folder and validate_path(folder):
            self.config["default_save_folder"] = folder
            self.path_label.configure(text=f"Default: {folder}")
            self.status_label.configure(text="Save folder set", text_color="green")
            from src.utils import save_config
            save_config(self.config)
        else:
            self.status_label.configure(text="Invalid folder selected", text_color="red")

    def compare_images(self, img_path):
        try:
            original, converted = self.converter.get_comparison_images(img_path)
            if not converted:
                self.status_label.configure(text="Convert first", text_color="red")
                return

            # Resize images for display in the comparison window
            max_size = (500, 500)
            original.thumbnail(max_size, Image.Resampling.LANCZOS)
            converted.thumbnail(max_size, Image.Resampling.LANCZOS)

            tk_orig = ctk.CTkImage(light_image=original, size=original.size)
            tk_conv = ctk.CTkImage(light_image=converted, size=converted.size)

            win = Toplevel(self)
            win.title("🔚 Image Comparison")
            win.geometry("1200x600")
            win.resizable(False, False)

            # Original image with label
            original_frame = ctk.CTkFrame(win, corner_radius=10)
            original_frame.pack(side="left", padx=20, pady=20, expand=True, fill="both")
            original_label = ctk.CTkLabel(original_frame, text="Original", font=("Arial", 16, "bold"))
            original_label.pack(pady=(10, 5))
            original_image_label = ctk.CTkLabel(original_frame, image=tk_orig, text="")
            original_image_label.image = tk_orig  # Keep a reference to avoid garbage collection
            original_image_label.pack()

            # Converted image with label
            converted_frame = ctk.CTkFrame(win, corner_radius=10)
            converted_frame.pack(side="right", padx=20, pady=20, expand=True, fill="both")
            converted_label = ctk.CTkLabel(converted_frame, text="Converted", font=("Arial", 16, "bold"))
            converted_label.pack(pady=(10, 5))
            converted_image_label = ctk.CTkLabel(converted_frame, image=tk_conv, text="")
            converted_image_label.image = tk_conv  # Keep a reference to avoid garbage collection
            converted_image_label.pack()
        except Exception as e:
            self.logger.error(f"Error comparing images {img_path}: {str(e)}")
            self.status_label.configure(text="Compare error", text_color="red")
            
            
class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
            
    