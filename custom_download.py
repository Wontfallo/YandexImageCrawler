"""
Customizable script for downloading images from Yandex.
Edit the configuration variables below to customize your download.
"""

from yandex_images_crawler.download import download
from pathlib import Path
import os
import time

# ======= CONFIGURATION - EDIT THESE VALUES =======

# Search term or full Yandex search URL
# Examples:
#   "cute dogs"
#   "landscape photography"
#   "https://yandex.com/images/search?text=mountain%20view&isize=large"
SEARCH = "cute cats"

# Number of images to download (set to 0 for unlimited)
NUMBER_OF_IMAGES = 10

# Minimum image size (width x height in pixels)
MIN_WIDTH = 800
MIN_HEIGHT = 600

# Output directory where images will be saved
OUTPUT_DIRECTORY = "downloaded_images"

# Run in headless mode (no browser window)
# Set to True to run without showing browser windows
HEADLESS_MODE = False

# Number of loader processes per link (1-4)
# Higher values may download faster but use more system resources
LOADERS_PER_LINK = 2

# ======= END OF CONFIGURATION =======

def main():
    # Create the search URL if a simple search term was provided
    search_url = SEARCH
    if not search_url.startswith("http"):
        search_url = f"https://yandex.com/images/search?text={SEARCH.replace(' ', '%20')}"
    
    # Create output directory
    output_path = Path(OUTPUT_DIRECTORY)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get list of existing files to skip
    skip_files = set()
    for _, _, files in os.walk(output_path):
        skip_files.update([file.split(".")[0] for file in files])
        break
    
    print(f"Starting download of {NUMBER_OF_IMAGES if NUMBER_OF_IMAGES > 0 else 'unlimited'} images")
    print(f"Search: {SEARCH}")
    print(f"Images will be saved to: {OUTPUT_DIRECTORY}")
    print(f"Minimum image size: {MIN_WIDTH}x{MIN_HEIGHT}")
    if not HEADLESS_MODE:
        print("This will open a Chrome browser window. Please don't close it until the download is complete.")
    print("Press Ctrl+C to cancel the download at any time.")
    print()
    
    try:
        # Start the download
        start_time = time.time()
        
        download(
            links=[search_url],
            image_size=(MIN_WIDTH, MIN_HEIGHT),
            image_count=NUMBER_OF_IMAGES,
            image_dir=output_path,
            skip_files=frozenset(skip_files),
            loaders_per_link=LOADERS_PER_LINK,
            headless_mode=HEADLESS_MODE
        )
        
        elapsed_time = time.time() - start_time
        
        # Count the number of downloaded images
        new_files = 0
        for _, _, files in os.walk(output_path):
            new_files = len(files) - len(skip_files)
            break
        
        print(f"\nDownload complete! Downloaded {new_files} new images in {elapsed_time:.1f} seconds.")
        print(f"Images are saved in the '{OUTPUT_DIRECTORY}' directory.")
        
    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
    except Exception as e:
        print(f"\nError during download: {e}")
        print("\nMake sure you have Chrome and ChromeDriver installed for Selenium.")
        print("If you're seeing Selenium errors, check that your ChromeDriver version matches your Chrome browser version.")

if __name__ == "__main__":
    main()
