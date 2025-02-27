"""
Example script demonstrating how to use the Yandex Images Crawler
to download a limited number of images from a Yandex search.
"""

import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Download images from Yandex search")
    parser.add_argument(
        "--search", 
        type=str, 
        required=True,
        help="Search term or full Yandex Images search URL"
    )
    parser.add_argument(
        "--count", 
        type=int, 
        default=10,
        help="Number of images to download (default: 10)"
    )
    parser.add_argument(
        "--size", 
        type=str, 
        default="0x0",
        help="Minimum image size in format WxH (e.g., 800x600). Default: no size limit (0x0)"
    )
    parser.add_argument(
        "--dir", 
        type=str, 
        default="downloaded_images",
        help="Directory to save downloaded images (default: downloaded_images)"
    )
    parser.add_argument(
        "--headless", 
        action="store_true",
        help="Run in headless mode (no browser UI)"
    )
    
    args = parser.parse_args()
    
    # Check if the search is a URL or a search term
    if args.search.startswith("http"):
        search_url = args.search
    else:
        # Create a Yandex search URL from the search term
        search_term = args.search.replace(" ", "%20")
        search_url = f"https://yandex.com/images/search?text={search_term}"
    
    # Prepare the command to run the Yandex Images Crawler
    cmd = [
        "yandex-images-crawler",
        "--links", search_url,
        "--count", str(args.count),
        "--size", args.size,
        "--dir", args.dir
    ]
    
    if args.headless:
        cmd.append("--headless")
    
    print(f"Starting download of {args.count} images for search: {args.search}")
    print(f"Images will be saved to: {args.dir}")
    print(f"Minimum image size: {args.size}")
    
    try:
        # Run the Yandex Images Crawler
        subprocess.run(cmd)
        print(f"\nDownload complete! Check the '{args.dir}' directory for your images.")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have installed the package with: pip install yandex-images-crawler")
        print("And that you have Chrome and ChromeDriver installed for Selenium.")
        sys.exit(1)

if __name__ == "__main__":
    main()
