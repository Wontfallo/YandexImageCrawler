"""
Example script that uses webdriver-manager to automatically handle ChromeDriver installation.
This makes it easier to get started without having to manually install ChromeDriver.
"""

from yandex_images_crawler.download import download
from pathlib import Path
import os
import time
import subprocess
import sys

# First, ensure webdriver-manager is installed
try:
    import webdriver_manager
except ImportError:
    print("Installing webdriver-manager...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])

# Now we can safely import and use it
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def download_with_auto_webdriver(
    search_term: str,
    count: int = 10,
    min_size: tuple = (0, 0),
    output_dir: str = "downloaded_images",
    headless: bool = False
):
    """
    Download images from Yandex search using automatic ChromeDriver management.
    
    Args:
        search_term: Search term or Yandex Images search URL
        count: Number of images to download
        min_size: Minimum image size as (width, height)
        output_dir: Directory to save downloaded images
        headless: Whether to run in headless mode
    """
    # Create the search URL if a simple search term was provided
    if not search_term.startswith("http"):
        search_url = f"https://yandex.com/images/search?text={search_term.replace(' ', '%20')}"
    else:
        search_url = search_term
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get list of existing files to skip
    skip_files = set()
    for _, _, files in os.walk(output_path):
        skip_files.update([file.split(".")[0] for file in files])
        break
    
    print(f"Starting download of {count} images of '{search_term}'")
    print(f"Images will be saved to: {output_dir}")
    print(f"Minimum image size: {min_size[0]}x{min_size[1]}")
    print("Using webdriver-manager to automatically handle ChromeDriver installation")
    if not headless:
        print("This will open a Chrome browser window. Please don't close it until the download is complete.")
    print("Press Ctrl+C to cancel the download at any time.")
    print()
    
    try:
        # Install ChromeDriver using webdriver-manager
        print("Setting up ChromeDriver...")
        # This will download the appropriate ChromeDriver version if needed
        chrome_driver_path = ChromeDriverManager().install()
        print(f"ChromeDriver installed at: {chrome_driver_path}")
        
        # Start the download
        start_time = time.time()
        
        # Override the default ChromeDriver path in the environment
        os.environ["PATH"] = os.path.dirname(chrome_driver_path) + os.pathsep + os.environ["PATH"]
        
        download(
            links=[search_url],
            image_size=min_size,
            image_count=count,
            image_dir=output_path,
            skip_files=frozenset(skip_files),
            loaders_per_link=2,
            headless_mode=headless
        )
        
        elapsed_time = time.time() - start_time
        
        # Count the number of downloaded images
        new_files = 0
        for _, _, files in os.walk(output_path):
            new_files = len(files) - len(skip_files)
            break
        
        print(f"\nDownload complete! Downloaded {new_files} new images in {elapsed_time:.1f} seconds.")
        print(f"Images are saved in the '{output_dir}' directory.")
        
    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
    except Exception as e:
        print(f"\nError during download: {e}")
        print("\nMake sure you have Chrome installed.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download images from Yandex with automatic ChromeDriver management")
    parser.add_argument("--search", type=str, default="cute cats", help="Search term or URL")
    parser.add_argument("--count", type=int, default=10, help="Number of images to download")
    parser.add_argument("--width", type=int, default=800, help="Minimum image width")
    parser.add_argument("--height", type=int, default=600, help="Minimum image height")
    parser.add_argument("--dir", type=str, default="downloaded_images", help="Output directory")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    download_with_auto_webdriver(
        search_term=args.search,
        count=args.count,
        min_size=(args.width, args.height),
        output_dir=args.dir,
        headless=args.headless
    )
