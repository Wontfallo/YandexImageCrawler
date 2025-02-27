"""
Installation script for Yandex Images Crawler dependencies.
This script checks for and installs the required dependencies.
"""

import subprocess
import sys
import os
import platform
import webbrowser

def check_python_version():
    """Check if Python version is 3.6 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("Error: Python 3.6 or higher is required.")
        print(f"Current Python version: {version.major}.{version.minor}.{version.micro}")
        return False
    return True

def install_package(package):
    """Install a Python package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        print(f"Error: Failed to install {package}.")
        return False

def check_chrome_installed():
    """Check if Chrome is installed."""
    system = platform.system()
    
    if system == "Windows":
        chrome_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Google\\Chrome\\Application\\chrome.exe"),
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                return True
    elif system == "Darwin":  # macOS
        if os.path.exists("/Applications/Google Chrome.app"):
            return True
    elif system == "Linux":
        try:
            subprocess.check_call(["which", "google-chrome"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            pass
    
    print("Chrome browser not found. Please install Chrome.")
    print("Opening Chrome download page...")
    webbrowser.open("https://www.google.com/chrome/")
    return False

def main():
    print("Checking and installing dependencies for Yandex Images Crawler...")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check if Chrome is installed
    chrome_installed = check_chrome_installed()
    if not chrome_installed:
        print("Please install Chrome and run this script again.")
        return
    
    # Install required packages
    print("\nInstalling required Python packages...")
    packages = [
        "yandex-images-crawler",
        "selenium",
        "webdriver-manager"  # For automatic ChromeDriver management
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        if not install_package(package):
            print(f"Failed to install {package}. Please install it manually.")
            return
    
    print("\nInstalling webdriver-manager to automatically manage ChromeDriver...")
    if not install_package("webdriver-manager"):
        print("Failed to install webdriver-manager. You'll need to install ChromeDriver manually.")
        print("Opening ChromeDriver download page...")
        webbrowser.open("https://chromedriver.chromium.org/downloads")
        return
    
    print("\nAll dependencies installed successfully!")
    print("\nYou can now use the Yandex Images Crawler with the provided scripts:")
    print("1. Run 'python custom_download.py' to download images with customizable settings")
    print("2. Run 'python download_cat_images.py' for a quick example")
    print("3. Run 'python example_usage.py --search \"your search term\" --count 10' for command-line usage")

if __name__ == "__main__":
    main()
