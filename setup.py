from cx_Freeze import setup, Executable
import sys
import os

# Include any necessary files (e.g., data, config, WebDriver)
include_files = ['./webdriver/chromedriver.exe', '.env']

# Set the base to "Console" for non-GUI apps or "Win32GUI" for GUI apps
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # For GUI apps

# Define the executables
executables = [Executable('gui.py', base=base,  icon="icon.ico")]

# Define the build options
build_options = {
    "packages": ["selenium", "webdriver_manager"],  # Include necessary packages
    "excludes": [],  # Exclude unnecessary packages (e.g., tkinter)
    "include_files": include_files,  # Include external files like WebDriver, etc.
    "zip_includes": [],  # Include any other dependencies as needed
}

# Run the setup
setup(
    name="Free Translator App",
    version="1.0",
    description="A translation app using Selenium and WebDriver",
    options={"build_exe": build_options},
    executables=executables,
)
