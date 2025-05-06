import os
import threading
from tkinter import filedialog, Toplevel
import customtkinter as ctk
from PIL import Image
from src.converter import ImageConverter
from src.utils import validate_path
import logging

class ImageConverterGUI(ctk.CTk):
    def __init__(self, config):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.converter = ImageConverter()
        self.uploaded_images = []
        self.title("Convo-Local")
        self.geometry("1300x750")
        self.minsize(1000, 600)
        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):
        ctk.set_appearance_mode("System")
        theme_path = os.path.join(os.path.dirname(__file__), "assets", "theme.json")
        if os.path.exists(theme_path):
            ctk.set_default_color_theme(theme_path)
        else:
            ctk.set_default_color_theme("green")

    def create_widgets(self):
        # Sidebar (left panel)
        self.left_panel = ctk.CTkFrame(self, width=260, corner_radius=15)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)

        # Main content (right panel)
        self.right_panel = ctk.CTkFrame(self, corner_radius=15)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Theme toggle button
        self.theme_btn = ctk.CTkButton(self.left_panel, text="🌗 Toggle Theme", command=self.toggle_theme)
        self.theme_btn.pack(pady=(10, 5), fill="x")

        # Buttons
        self.upload_btn = ctk.CTkButton(self.left_panel, text="📄 Upload Images", command=self.upload_images, hover_color="#2ecc71")
        self.upload_btn.pack(pady=5, fill="x")

        self.convert_btn = ctk.CTkButton(self.left_panel, text="⚙️ Convert All", command=self.start_conversion, hover_color="#3498db")
        self.convert_btn.pack(pady=5, fill="x")

        self.save_btn = ctk.CTkButton(self.left_panel, text="💾 Save Converted", command=self.save_converted_images, hover_color="#e74c3c")
        self.save_btn.pack(pady=5, fill="x")

        self.set_folder_btn = ctk.CTkButton(self.left_panel, text="📁 Set Save Folder", command=self.set_save_folder, hover_color="#f1c40f")
        self.set_folder_btn.pack(pady=5, fill="x")

        # Save folder path
        self.path_label = ctk.CTkLabel(self.left_panel, text=f"Default: {self.config.get('default_save_folder', 'Not set')}", wraplength=220)
        self.path_label.pack(pady=(10, 5))

        # Progress bar
        self.progress = ctk.CTkProgressBar(self.left_panel, height=10)
        self.progress.set(0)
        self.progress.pack(pady=(10, 5), fill="x")

        # Status label
        self.status_label = ctk.CTkLabel(self.left_panel, text="", wraplength=220, text_color="white")
        self.status_label.pack(pady=(5, 10))

        # Thumbnail panel (grid layout)
        self.thumb_panel = ctk.CTkScrollableFrame(self.right_panel, corner_radius=15)
        self.thumb_panel.pack(fill="both", expand=True, padx=10, pady=10)
        self.thumb_panel.grid_columnconfigure((0, 1, 2), weight=1)

    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "Dark" if current_mode == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)
        self.status_label.configure(text=f"Switched to {new_mode} mode", text_color="green")

    def upload_images(self):
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.heic")])
        if paths:
            for path in paths:
                if validate_path(path):
                    self.uploaded_images.append(path)
                    threading.Thread(target=self.add_thumbnail, args=(path,)).start()
                else:
                    self.status_label.configure(text=f"Invalid path: {path}", text_color="red")

    def add_thumbnail(self, img_path):
        row = len(self.uploaded_images) // 3
        col = len(self.uploaded_images) % 3
        frame = ctk.CTkFrame(self.thumb_panel, corner_radius=10)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        try:
            img = Image.open(img_path)
            img.thumbnail((120, 120))
            thumb_img = ctk.CTkImage(light_image=img, size=img.size)
            img_button = ctk.CTkButton(
                frame, image=thumb_img, text=os.path.basename(img_path), compound="top",
                command=lambda p=img_path: self.open_full_image(p), anchor="center",
                fg_color="transparent", hover_color="#e2e8f0"
            )
            img_button.pack(pady=5)

            compare_btn = ctk.CTkButton(frame, text="🔚 Compare", width=100, command=lambda p=img_path: self.compare_images(p))
            compare_btn.pack(pady=5)
        except Exception as e:
            self.logger.error(f"Error loading thumbnail {img_path}: {str(e)}")
            self.status_label.configure(text=f"Error loading {os.path.basename(img_path)}", text_color="red")

    def open_full_image(self, img_path):
        try:
            img = Image.open(img_path)
            w, h = img.size
            if w > 1000 or h > 1000:
                img.thumbnail((1000, 1000))
            tk_img = ctk.CTkImage(light_image=img, size=img.size)
            win = Toplevel(self)
            win.title("🖼️ Full Size Image")
            label = ctk.CTkLabel(win, image=tk_img, text="", anchor="center")
            label.image = tk_img
            label.pack(expand=True)
        except Exception as e:
            self.logger.error(f"Error opening full image {img_path}: {str(e)}")
            self.status_label.configure(text=f"Error opening image", text_color="red")

    def start_conversion(self):
        if not self.uploaded_images:
            self.status_label.configure(text="Upload images first", text_color="red")
            return
        threading.Thread(target=self.convert_images).start()

    def convert_images(self):
        self.converter.clear_converted()
        total = len(self.uploaded_images)
        for idx, img_path in enumerate(self.uploaded_images):
            try:
                self.converter.convert_image(img_path)
                self.progress.set((idx + 1) / total)
            except Exception as e:
                self.logger.error(f"Error converting {img_path}: {str(e)}")
        self.status_label.configure(text=f"Converted {len(self.converter.converted_images)} images", text_color="green")

    def save_converted_images(self):
        if not self.converter.converted_images:
            self.status_label.configure(text="No converted images to save", text_color="red")
            return
        folder = self.config.get("default_save_folder") or filedialog.askdirectory()
        if not folder:
            return
        try:
            self.converter.save_converted(folder)
            self.status_label.configure(text=f"Saved to {folder}", text_color="green")
        except Exception as e:
            self.logger.error(f"Error saving images: {str(e)}")
            self.status_label.configure(text=f"Error saving images", text_color="red")

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

            original.thumbnail((500, 500))
            converted.thumbnail((500, 500))

            tk_orig = ctk.CTkImage(light_image=original, size=original.size)
            tk_conv = ctk.CTkImage(light_image=converted, size=converted.size)

            win = Toplevel(self)
            win.title("🔚 Image Comparison")
            win.geometry("1100x550")

            l1 = ctk.CTkLabel(win, text="Original", image=tk_orig, compound="top")
            l1.pack(side="left", padx=20, pady=20)

            l2 = ctk.CTkLabel(win, text="Converted", image=tk_conv, compound="top")
            l2.pack(side="right", padx=20, pady=20)
        except Exception as e:
            self.logger.error(f"Error comparing images {img_path}: {str(e)}")
            self.status_label.configure(text=f"Compare error", text_color="red")