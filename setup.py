from setuptools import setup

setup(
    name="Convo",
    version="1.0.0",
    description="A universal image converter for HEIC, PNG, JPEG",
    author="Lhasang Lama",
    author_email="lamalhasang256@gmail.com",
    packages=["src"],
    install_requires=[
        "customtkinter",
        "Pillow",
        "pillow",
        "pyinstaller",
    ],
    entry_points={
        "console_scripts": [
            "image-converter=src.main:main",
        ]
    },
)