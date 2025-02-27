"""
Safe version of the Yandex Images Crawler with error handling and graceful exit.
This script will automatically stop if too many errors occur in succession.
"""

import argparse
import logging
import os
import signal
import sys
import time
from multiprocessing import Process, Queue, Value
from pathlib import Path

# First, ensure webdriver-manager is installed
try:
    import webdriver_manager
except ImportError:
    print("Installing webdriver-manager...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])

# Import the crawler components
try:
    from yandex_images_crawler.count_checker import CountChecker
    from yandex_images_crawler.image_loader import ImageLoader
    from yandex_images_crawler.yandex_crawler import YandexCrawler
except ImportError:
    print("Installing yandex-images-crawler...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yandex-images-crawler"])
    from yandex_images_crawler.count_checker import CountChecker
    from yandex_images_crawler.image_loader import ImageLoader
    from yandex_images_crawler.yandex_crawler import YandexCrawler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global flag to track if we should exit
should_exit = False

class SafeYandexCrawler(YandexCrawler):
    """
    Extended version of YandexCrawler with additional error handling.
    """
    def __init__(self, *args, max_errors=10, **kwargs):
        super().__init__(*args, **kwargs)
        self.consecutive_errors = 0
        self.max_errors = max_errors
        
    def run(self):
        global should_exit
        self.driver.get(self.start_link)
        
        try:
            self._SafeYandexCrawler__open_first_preview()
        except Exception as e:
            self.logger.critical(f"Process #{self.id} can't open the first image: {e}")
            self.logger.info("Exiting crawler due to initial error")
            self.is_active.value = False
            should_exit = True
            self.driver.close()
            return
        
        while True:
            if not self.is_active.value or should_exit:
                self.logger.info(f"Process #{self.id} shutting down")
                self.driver.close()
                return
            
            try:
                self._YandexCrawler__get_image_link()
                self._YandexCrawler__open_next_preview()
                # Reset error counter on success
                self.consecutive_errors = 0
            except Exception as e:
                self.consecutive_errors += 1
                self.logger.critical(f"Process #{self.id} error: {e}")
                
                if self.consecutive_errors >= self.max_errors:
                    self.logger.critical(f"Process #{self.id} reached max consecutive errors ({self.max_errors}). Shutting down.")
                    self.is_active.value = False
                    should_exit = True
                    self.driver.close()
                    return
                
                time.sleep(2)  # Wait a bit before retrying

def __start_safe_crawler(
    start_link: str, load_queue: Queue, id: int, headless_mode: bool, is_active, max_errors: int
):
    crawler = SafeYandexCrawler(
        start_link=start_link,
        load_queue=load_queue,
        id=id,
        headless_mode=headless_mode,
        is_active=is_active,
        max_errors=max_errors
    )
    crawler.run()

def safe_download(
    links,
    image_size=(0, 0),
    image_count=10,
    image_dir="downloaded_images",
    skip_files=frozenset(),
    loaders_per_link=1,
    headless_mode=False,
    max_errors=10,
    timeout=300  # 5 minutes timeout
):
    """
    Safe version of the download function with error handling and timeout.
    
    Args:
        links: List of Yandex search URLs
        image_size: Minimum image size as (width, height)
        image_count: Number of images to download (0 for unlimited)
        image_dir: Directory to save downloaded images
        skip_files: Set of file hashes to skip
        loaders_per_link: Number of loader processes per link
        headless_mode: Whether to run in headless mode
        max_errors: Maximum number of consecutive errors before exiting
        timeout: Maximum time in seconds to run before exiting
    """
    proc_num = len(links)
    load_queue = Queue(10 * proc_num)
    is_active = Value("i", True)
    
    # Create output directory
    Path(image_dir).mkdir(parents=True, exist_ok=True)
    
    # Set up signal handler for graceful exit
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal. Shutting down...")
        is_active.value = False
        global should_exit
        should_exit = True
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create crawler processes
    crawlers = [
        Process(
            target=__start_safe_crawler,
            args=(links[i], load_queue, i, headless_mode, is_active, max_errors),
            daemon=True,
        )
        for i in range(proc_num)
    ]
    
    # Create loader processes
    loaders = [
        Process(
            target=__start_loader,
            args=(load_queue, image_size, image_dir, skip_files, is_active),
            daemon=True,
        )
        for _ in range(proc_num * loaders_per_link)
    ]
    
    # Create checker process
    checker = Process(
        target=__start_checker,
        args=(image_dir, image_count, is_active),
        daemon=True,
    )
    
    # Start all processes
    processes = []
    processes.extend(crawlers)
    processes.extend(loaders)
    processes.append(checker)
    
    for process in processes:
        process.start()
    
    # Monitor processes and implement timeout
    start_time = time.time()
    try:
        while any(p.is_alive() for p in processes):
            # Check if we should exit
            if should_exit or not is_active.value:
                logger.info("Stopping all processes...")
                is_active.value = False
                break
            
            # Check timeout
            if timeout > 0 and time.time() - start_time > timeout:
                logger.info(f"Reached timeout of {timeout} seconds. Shutting down...")
                is_active.value = False
                break
            
            # Count downloaded images
            downloaded = 0
            for _, _, files in os.walk(image_dir):
                downloaded = len(files) - len(skip_files)
                break
            
            logger.info(f"Downloaded {downloaded} images so far...")
            
            time.sleep(5)  # Check status every 5 seconds
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
        is_active.value = False
    finally:
        # Wait for processes to terminate
        is_active.value = False
        
        # Give processes a chance to terminate gracefully
        for i in range(5):
            if not any(p.is_alive() for p in processes):
                break
            time.sleep(1)
        
        # Force terminate any remaining processes
        for p in processes:
            if p.is_alive():
                p.terminate()
        
        # Count final number of downloaded images
        downloaded = 0
        for _, _, files in os.walk(image_dir):
            downloaded = len(files) - len(skip_files)
            break
        
        logger.info(f"Download complete. Downloaded {downloaded} images.")

# Helper functions from the original download.py
def __start_loader(
    load_queue: Queue,
    image_size,
    image_dir,
    skip_files,
    is_active,
):
    crawler = ImageLoader(
        load_queue=load_queue,
        image_size=image_size,
        image_dir=image_dir,
        skip_files=skip_files,
        is_active=is_active,
    )
    crawler.run()

def __start_checker(image_dir, image_count, is_active):
    checker = CountChecker(
        image_dir=image_dir,
        image_count=image_count,
        is_active=is_active,
    )
    checker.run()

def main():
    parser = argparse.ArgumentParser(description="Safe Yandex Images Crawler")
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
        help="Number of images to download (default: 10, 0 for unlimited)"
    )
    parser.add_argument(
        "--size",
        type=str,
        default="0x0",
        help="Minimum image size in format WxH (e.g., 800x600)"
    )
    parser.add_argument(
        "--dir",
        type=str,
        default="downloaded_images",
        help="Directory to save downloaded images"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (no browser UI)"
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=10,
        help="Maximum number of consecutive errors before exiting"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Maximum time in seconds to run before exiting (0 for no timeout)"
    )
    
    args = parser.parse_args()
    
    # Process search term or URL
    if args.search.startswith("http"):
        search_url = args.search
    else:
        search_url = f"https://yandex.com/images/search?text={args.search.replace(' ', '%20')}"
    
    # Process image size
    try:
        width, height = map(int, args.size.split("x"))
        image_size = (width, height)
    except ValueError:
        logger.error(f"Invalid size format: {args.size}. Using default 0x0.")
        image_size = (0, 0)
    
    # Get list of existing files to skip
    skip_files = set()
    for _, _, files in os.walk(args.dir):
        skip_files.update([file.split(".")[0] for file in files])
        break
    
    print(f"Starting download of {args.count if args.count > 0 else 'unlimited'} images")
    print(f"Search: {args.search}")
    print(f"Images will be saved to: {args.dir}")
    print(f"Minimum image size: {image_size[0]}x{image_size[1]}")
    print(f"Maximum consecutive errors: {args.max_errors}")
    print(f"Timeout: {args.timeout} seconds (0 means no timeout)")
    if not args.headless:
        print("This will open a Chrome browser window. Please don't close it until the download is complete.")
    print("Press Ctrl+C to cancel the download at any time.")
    print()
    
    # Start the download
    safe_download(
        links=[search_url],
        image_size=image_size,
        image_count=args.count,
        image_dir=args.dir,
        skip_files=frozenset(skip_files),
        loaders_per_link=2,
        headless_mode=args.headless,
        max_errors=args.max_errors,
        timeout=args.timeout
    )

if __name__ == "__main__":
    main()
