# Convo

A user-friendly desktop application to convert images (JPG, PNG, HEIC) to JPEG, with features for batch conversion, image comparison, and customizable save locations.

## Problem

Many users, especially on Windows, struggle with HEIC images (common on iPhones) due to limited native support. Existing converters are often complex, lack batch processing, or have outdated interfaces. I needed a simple, modern tool to convert HEIC and other formats to JPEG efficiently.

## Solution

The Universal Image Converter solves this by providing:

- **Batch Conversion**: Convert multiple images (JPG, PNG, HEIC) to JPEG in one go.
- **Modern UI**: Clean, responsive interface with light/dark mode and tooltips.
- **Image Comparison**: View original and converted images side-by-side.
- **Custom Save Folder**: Set a default save location for convenience.
- **Robustness**: Error handling and logging for reliable operation.

---

## Installation (For Developers)

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/Convo.git
    cd Convo
    ```

2. **Create a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:

   ```bash
   python src/main.py
   ```

## Distribution (For Users)

1. **Download the Executable**:

   - Visit the Releases page.
   - Download the latest `main.exe` (Windows) or the zipped `main` folder.
   - No installation or Python required!

2. **Run the App**:

   - Double-click `main.exe` (single-file) or `main/main.exe` (folder).
   - On Windows, you may see a “Windows protected your PC” warning. Click **“More info” > “Run anyway”**.

3. **System Requirements**:

   - Windows 10 or later (macOS/Linux support planned).
   - 100 MB free disk space.

---

## Building the Executable (For Developers)

To create a standalone `.exe` (Windows):

1. Install `PyInstaller`:

   ```bash
   pip install pyinstaller
2. Build the executable:

   ```bash
   pyinstaller --icon=src/assets/icon.ico --noconsole src/main.py
   ```
3. Find the executable in `dist/main/` or `dist/main.exe` (if using `--onefile`).

## Usage

1. **Upload Images**: Click "Upload Images" to select JPG, PNG, or HEIC files.
2. **Convert**: Click "Convert All" to convert images to JPEG.
3. **Compare**: Use the "Compare" button to view original vs. converted images.
4. **Save**: Click "Save Converted" to save images to the default or a selected folder.
5. **Set Folder**: Set a default save folder for convenience.
6. **Toggle Theme**: Switch between light and dark modes.

## Screenshots

*(Add your screenshot here)*

## Contributing

Contributions are welcome! Please:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See LICENSE for details.