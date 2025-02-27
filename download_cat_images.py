"""
Ready-to-run example that downloads 10 cat images from Yandex.
Just run this script directly to download the images.
"""

from yandex_images_crawler.download import download
from pathlib import Path
import os
import time

def main():
    # Configuration
    search_term = "cute cats"
    num_images = 10
    output_dir = "cat_images"
    min_width = 800
    min_height = 600
    
    # Create the search URL
    search_url = f"https://yandex.com/images/search?text={search_term.replace(' ', '%20')}"
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get list of existing files to skip
    skip_files = set()
    for _, _, files in os.walk(output_path):
        skip_files.update([file.split(".")[0] for file in files])
        break
    
    print(f"Starting download of {num_images} images of '{search_term}'")
    print(f"Images will be saved to: {output_dir}")
    print(f"Minimum image size: {min_width}x{min_height}")
    print("This will open a Chrome browser window. Please don't close it until the download is complete.")
    print("Press Ctrl+C to cancel the download at any time.")
    print()
    
    try:
        # Start the download
        start_time = time.time()
        
        download(
            links=[search_url],
            image_size=(min_width, min_height),
            image_count=num_images,
            image_dir=output_path,
            skip_files=frozenset(skip_files),
            loaders_per_link=2,  # Use 2 loaders for faster downloads
            headless_mode=False  # Set to True for headless mode
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
        print("\nMake sure you have Chrome and ChromeDriver installed for Selenium.")

if __name__ == "__main__":
    main()
