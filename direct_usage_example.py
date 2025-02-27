"""
Example script demonstrating how to use the Yandex Images Crawler directly
in Python code (not just as a command-line tool).
"""

from yandex_images_crawler.download import download
from pathlib import Path
import os

def download_images(
    search_url: str,
    count: int = 10,
    min_size: tuple = (0, 0),
    output_dir: str = "downloaded_images",
    headless: bool = False
):
    """
    Download images from Yandex search using the crawler directly.
    
    Args:
        search_url: Yandex Images search URL
        count: Number of images to download
        min_size: Minimum image size as (width, height)
        output_dir: Directory to save downloaded images
        headless: Whether to run in headless mode
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get list of existing files to skip
    skip_files = set()
    for _, _, files in os.walk(output_path):
        skip_files.update([file.split(".")[0] for file in files])
        break
    
    # Convert skip_files to frozenset as required by the download function
    skip_files_frozen = frozenset(skip_files)
    
    # Call the download function
    download(
        links=[search_url],  # List of search URLs
        image_size=min_size,  # Minimum image size (width, height)
        image_count=count,    # Number of images to download
        image_dir=output_path,  # Output directory
        skip_files=skip_files_frozen,  # Files to skip
        loaders_per_link=1,   # Number of loader processes per link
        headless_mode=headless  # Whether to run in headless mode
    )

if __name__ == "__main__":
    # Example 1: Download 5 cat images
    search_url = "https://yandex.com/images/search?text=cats"
    download_images(
        search_url=search_url,
        count=5,
        output_dir="cat_images"
    )
    
    # Example 2: Download 10 landscape images with minimum size 1920x1080
    # Uncomment to run this example
    """
    search_url = "https://yandex.com/images/search?text=landscape%20photography"
    download_images(
        search_url=search_url,
        count=10,
        min_size=(1920, 1080),
        output_dir="landscape_images",
        headless=True  # Run in headless mode
    )
    """
