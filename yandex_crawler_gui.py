"""
GUI application for Yandex Images Crawler.
This provides a user-friendly interface for downloading images from Yandex.
"""

import os
import sys
import time
import signal
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Ensure required packages are installed
def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

required_packages = ["yandex-images-crawler", "selenium", "webdriver-manager"]
for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
    except ImportError:
        print(f"Installing {package}...")
        if not install_package(package):
            messagebox.showerror("Installation Error", f"Failed to install {package}. Please install it manually.")
            sys.exit(1)

# Now we can safely import the required modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

class YandexCrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Yandex Images Crawler")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Set theme and style
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use 'clam' theme for a modern look
        
        # Configure colors
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('TProgressbar', thickness=20)
        
        # Variables
        self.search_var = tk.StringVar(value="cute cats")
        self.count_var = tk.StringVar(value="10")
        self.width_var = tk.StringVar(value="800")
        self.height_var = tk.StringVar(value="600")
        self.output_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "downloaded_images"))
        self.headless_var = tk.BooleanVar(value=False)
        self.max_errors_var = tk.StringVar(value="10")
        self.timeout_var = tk.StringVar(value="300")
        
        # Download status variables
        self.is_downloading = False
        self.download_thread = None
        self.stop_event = threading.Event()
        self.driver = None
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create and place widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = ttk.Label(self.main_frame, text="Yandex Images Crawler", style='Header.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        # Search term
        ttk.Label(self.main_frame, text="Search Term or URL:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(self.main_frame, textvariable=self.search_var, width=50).grid(row=1, column=1, columnspan=2, sticky="we", pady=5)
        
        # Number of images
        ttk.Label(self.main_frame, text="Number of Images:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(self.main_frame, textvariable=self.count_var, width=10).grid(row=2, column=1, sticky="w", pady=5)
        ttk.Label(self.main_frame, text="(0 for unlimited)").grid(row=2, column=2, sticky="w", pady=5)
        
        # Minimum image size
        ttk.Label(self.main_frame, text="Minimum Image Size:").grid(row=3, column=0, sticky="w", pady=5)
        size_frame = ttk.Frame(self.main_frame)
        size_frame.grid(row=3, column=1, columnspan=2, sticky="w", pady=5)
        ttk.Entry(size_frame, textvariable=self.width_var, width=6).pack(side=tk.LEFT)
        ttk.Label(size_frame, text="×").pack(side=tk.LEFT, padx=5)
        ttk.Entry(size_frame, textvariable=self.height_var, width=6).pack(side=tk.LEFT)
        ttk.Label(size_frame, text="pixels").pack(side=tk.LEFT, padx=5)
        
        # Output directory
        ttk.Label(self.main_frame, text="Output Directory:").grid(row=4, column=0, sticky="w", pady=5)
        dir_frame = ttk.Frame(self.main_frame)
        dir_frame.grid(row=4, column=1, columnspan=2, sticky="we", pady=5)
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_directory).pack(side=tk.LEFT, padx=(5, 0))
        
        # Advanced options
        advanced_frame = ttk.LabelFrame(self.main_frame, text="Advanced Options")
        advanced_frame.grid(row=5, column=0, columnspan=3, sticky="we", pady=10)
        
        # Headless mode
        ttk.Checkbutton(advanced_frame, text="Headless Mode (no browser window)", variable=self.headless_var).grid(row=0, column=0, columnspan=2, sticky="w", pady=5, padx=5)
        
        # Max errors
        ttk.Label(advanced_frame, text="Max Consecutive Errors:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        ttk.Entry(advanced_frame, textvariable=self.max_errors_var, width=6).grid(row=1, column=1, sticky="w", pady=5)
        
        # Timeout
        ttk.Label(advanced_frame, text="Timeout (seconds):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        ttk.Entry(advanced_frame, textvariable=self.timeout_var, width=6).grid(row=2, column=1, sticky="w", pady=5)
        ttk.Label(advanced_frame, text="(0 for no timeout)").grid(row=2, column=2, sticky="w", pady=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(self.main_frame, text="Status")
        status_frame.grid(row=6, column=0, columnspan=3, sticky="we", pady=10)
        
        # Status text
        self.status_text = tk.Text(status_frame, height=10, width=60, wrap=tk.WORD)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(status_frame, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        # Progress bar
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.grid(row=7, column=0, columnspan=3, sticky="we", pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, sticky="we", pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Download", command=self.start_download)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Download", command=self.stop_download, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Exit", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Add some initial status text
        self.log_message("Ready to download images from Yandex.")
        self.log_message("Enter a search term or URL and click 'Start Download'.")
        
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        logger.info(message)
    
    def validate_inputs(self):
        # Check search term
        if not self.search_var.get().strip():
            messagebox.showerror("Input Error", "Please enter a search term or URL.")
            return False
        
        # Check count
        try:
            count = int(self.count_var.get())
            if count < 0:
                raise ValueError("Count must be a non-negative integer.")
        except ValueError:
            messagebox.showerror("Input Error", "Number of images must be a non-negative integer.")
            return False
        
        # Check width and height
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            if width < 0 or height < 0:
                raise ValueError("Width and height must be non-negative integers.")
        except ValueError:
            messagebox.showerror("Input Error", "Width and height must be non-negative integers.")
            return False
        
        # Check max errors
        try:
            max_errors = int(self.max_errors_var.get())
            if max_errors <= 0:
                raise ValueError("Max errors must be a positive integer.")
        except ValueError:
            messagebox.showerror("Input Error", "Max errors must be a positive integer.")
            return False
        
        # Check timeout
        try:
            timeout = int(self.timeout_var.get())
            if timeout < 0:
                raise ValueError("Timeout must be a non-negative integer.")
        except ValueError:
            messagebox.showerror("Input Error", "Timeout must be a non-negative integer.")
            return False
        
        # Check output directory
        output_dir = Path(self.output_dir_var.get())
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Directory Error", f"Could not create output directory: {e}")
            return False
        
        return True
    
    def start_download(self):
        if not self.validate_inputs():
            return
        
        if self.is_downloading:
            messagebox.showinfo("Download in Progress", "A download is already in progress.")
            return
        
        self.is_downloading = True
        self.stop_event.clear()
        
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
        # Clear status text
        self.status_text.delete(1.0, tk.END)
        
        # Start download in a separate thread
        self.download_thread = threading.Thread(target=self.download_images)
        self.download_thread.daemon = True
        self.download_thread.start()
        
        # Start progress update
        self.root.after(1000, self.update_progress)
    
    def stop_download(self):
        if not self.is_downloading:
            return
        
        self.log_message("Stopping download...")
        self.stop_event.set()
        
        # Wait for thread to finish
        if self.download_thread and self.download_thread.is_alive():
            self.download_thread.join(timeout=5.0)
        
        self.is_downloading = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.log_message("Download stopped.")
    
    def update_progress(self):
        if not self.is_downloading:
            return
        
        # Get count of downloaded images
        output_dir = Path(self.output_dir_var.get())
        if output_dir.exists():
            downloaded = len(list(output_dir.glob("*.png")))
            target_count = int(self.count_var.get())
            
            if target_count > 0:
                progress = min(100, int(downloaded / target_count * 100))
                self.progress_var.set(progress)
        
        # Schedule next update
        self.root.after(1000, self.update_progress)
    
    def download_images(self):
        try:
            # Get parameters
            search = self.search_var.get().strip()
            count = int(self.count_var.get())
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            output_dir = self.output_dir_var.get()
            headless = self.headless_var.get()
            max_errors = int(self.max_errors_var.get())
            timeout = int(self.timeout_var.get())
            
            # Create search URL if needed
            if not search.startswith("http"):
                search_url = f"https://yandex.com/images/search?text={search.replace(' ', '%20')}"
            else:
                search_url = search
            
            self.log_message(f"Starting download of {count if count > 0 else 'unlimited'} images")
            self.log_message(f"Search: {search}")
            self.log_message(f"Minimum image size: {width}x{height}")
            self.log_message(f"Output directory: {output_dir}")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("--incognito")
            if headless:
                chrome_options.add_argument("--headless")
            
            # Install ChromeDriver
            self.log_message("Setting up ChromeDriver...")
            chrome_driver_path = ChromeDriverManager().install()
            self.log_message(f"ChromeDriver installed at: {chrome_driver_path}")
            
            # Create WebDriver
            service = Service(chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            # Navigate to search URL
            self.log_message(f"Opening {search_url}")
            self.driver.get(search_url)
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Get initial file count
            initial_files = set()
            for _, _, files in os.walk(output_dir):
                initial_files.update([file.split(".")[0] for file in files])
                break
            
            # Check for CAPTCHA
            self.log_message("Checking for CAPTCHA...")
            try:
                # Look for common CAPTCHA elements
                captcha_elements = [
                    "//div[contains(@class, 'CheckboxCaptcha')]",
                    "//div[contains(@class, 'Captcha')]",
                    "//div[contains(@class, 'captcha')]",
                    "//iframe[contains(@src, 'captcha')]",
                    "//iframe[contains(@src, 'recaptcha')]",
                    "//div[contains(text(), 'robot')]",
                    "//div[contains(text(), 'CAPTCHA')]",
                    "//div[contains(text(), 'captcha')]"
                ]
                
                captcha_found = False
                for xpath in captcha_elements:
                    try:
                        elements = self.driver.find_elements("xpath", xpath)
                        if elements:
                            captcha_found = True
                            break
                    except:
                        pass
                
                if captcha_found:
                    self.log_message("CAPTCHA detected! Please solve the CAPTCHA manually.")
                    
                    # Show a message box to the user
                    self.root.after(0, lambda: messagebox.showinfo(
                        "CAPTCHA Detected", 
                        "Please solve the CAPTCHA in the browser window, then click OK to continue."
                    ))
                    
                    # Wait for user to solve CAPTCHA
                    self.log_message("Waiting for you to solve the CAPTCHA and click OK...")
                    
                    # Give some time for the page to load after CAPTCHA is solved
                    time.sleep(3)
                    self.log_message("Continuing after CAPTCHA...")
            except Exception as e:
                self.log_message(f"Error checking for CAPTCHA: {e}")
            
            # Open first image
            self.log_message("Opening first image...")
            try:
                # Try different selectors for the first image
                first_image_selectors = [
                    "img[class*='ImagesContentImage-Image_clickable']",
                    "img[class*='serp-item__thumb']",
                    ".serp-item__link",
                    ".serp-item",
                    "div[class*='serp-item']",
                    "div[data-grid-position]",
                    "a[href*='images/search'] img",
                    "div[class*='Image'] img"
                ]
                
                image_found = False
                for selector in first_image_selectors:
                    try:
                        self.log_message(f"Trying to find image with selector: {selector}")
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            self.log_message(f"Found {len(elements)} elements with selector: {selector}")
                            elements[0].click()
                            image_found = True
                            self.log_message("First image opened successfully.")
                            break
                    except Exception as e:
                        self.log_message(f"Selector {selector} failed: {e}")
                
                if not image_found:
                    # Try JavaScript click as a last resort
                    try:
                        self.log_message("Trying JavaScript click on first image...")
                        self.driver.execute_script("""
                            var images = document.querySelectorAll('img');
                            if (images.length > 0) {
                                images[0].click();
                                return true;
                            }
                            return false;
                        """)
                        time.sleep(2)  # Wait for the click to take effect
                        image_found = True
                        self.log_message("First image opened with JavaScript.")
                    except Exception as e:
                        self.log_message(f"JavaScript click failed: {e}")
                
                if not image_found:
                    # Show a message box to the user
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Manual Interaction Required", 
                        "Please click on the first image in the browser window, then click OK to continue."
                    ))
                    
                    # Wait for user to click the image
                    self.log_message("Waiting for you to click on the first image and then click OK...")
                    
                    # Give some time for the page to load after user interaction
                    time.sleep(3)
                    self.log_message("Continuing after manual interaction...")
                    image_found = True
                
                if not image_found:
                    raise Exception("Could not open the first image.")
                
                # Start downloading images
                start_time = time.time()
                consecutive_errors = 0
                downloaded = 0
                
                while not self.stop_event.is_set():
                    # Check timeout
                    if timeout > 0 and time.time() - start_time > timeout:
                        self.log_message(f"Reached timeout of {timeout} seconds.")
                        break
                    
                    # Check if we've downloaded enough images
                    if count > 0 and downloaded >= count:
                        self.log_message(f"Downloaded {downloaded} images. Target reached.")
                        break
                    
                    try:
                        # Get image link and size
                        width_found, height_found = None, None
                        
                        # Try to get image size
                        size_sources = [
                            "OpenImageButton-SizesButton",
                            "MMViewerButtons-ImageSizes",
                            "OpenImageButton-SaveSize",
                            "Button2-Text",
                        ]
                        
                        for source in size_sources:
                            if width_found is not None and height_found is not None:
                                break
                            for elem in self.driver.find_elements(By.CLASS_NAME, source):
                                try:
                                    width_found, height_found = [int(i) for i in elem.text.split("×")]
                                    break
                                except:
                                    pass
                        
                        if width_found is None or height_found is None:
                            raise Exception("Could not get image size.")
                        
                        # Get image link
                        link = None
                        link_sources = [
                            "OpenImageButton-Save",
                            "MMViewerButtons-OpenImage",
                            "MMViewerButtons-Button",
                            "Button2_link",
                            "Button2_view_default",
                        ]
                        
                        blacklist = [
                            "yandex-images",
                            "avatars.mds.yandex.net",
                        ]
                        
                        for source in link_sources:
                            if link is not None:
                                break
                            for elem in self.driver.find_elements(By.CLASS_NAME, source):
                                try:
                                    link = elem.get_attribute("href")
                                    for b in blacklist:
                                        if b in link:
                                            time.sleep(2)
                                            link = elem.get_attribute("href")
                                            break
                                    break
                                except:
                                    pass
                        
                        if link is None:
                            raise Exception("Could not get image link.")
                        
                        # Check if image meets size requirements
                        if width_found >= width and height_found >= height:
                            self.log_message(f"Found image: {width_found}x{height_found} - {link}")
                            
                            # Download image
                            try:
                                import requests
                                from PIL import Image
                                import io
                                import hashlib
                                import numpy as np
                                
                                headers = {
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
                                    "Referer": "https://yandex.com/",
                                }
                                
                                response = requests.get(link, headers=headers, verify=False, timeout=10)
                                
                                if 200 <= response.status_code < 300:
                                    img = Image.open(io.BytesIO(response.content))
                                    img_width, img_height = img.size
                                    
                                    if img_width >= width and img_height >= height:
                                        hash_name = hashlib.sha256(np.array(img)).hexdigest()
                                        img_path = output_path / (hash_name + ".png")
                                        
                                        if hash_name not in initial_files and not img_path.exists():
                                            img = img.convert("RGB")
                                            img.save(img_path, "PNG")
                                            downloaded += 1
                                            self.log_message(f"Downloaded image {downloaded}: {img_width}x{img_height}")
                                            consecutive_errors = 0
                            except Exception as e:
                                self.log_message(f"Error downloading image: {e}")
                        
                        # Move to next image
                        try:
                            btn = self.driver.find_element(
                                By.CSS_SELECTOR, "button[class*='CircleButton_type_next']"
                            )
                            btn.click()
                            time.sleep(1)  # Wait for the next image to load
                        except Exception as e:
                            raise Exception(f"Could not move to the next image: {e}")
                        
                    except Exception as e:
                        consecutive_errors += 1
                        self.log_message(f"Error: {e}")
                        
                        if consecutive_errors >= max_errors:
                            self.log_message(f"Reached maximum consecutive errors ({max_errors}). Stopping.")
                            break
                        
                        time.sleep(2)  # Wait before retrying
                
                elapsed_time = time.time() - start_time
                self.log_message(f"Download complete. Downloaded {downloaded} images in {elapsed_time:.1f} seconds.")
                
            except Exception as e:
                self.log_message(f"Error during download: {e}")
            
            finally:
                # Clean up
                if self.driver:
                    self.driver.quit()
                    self.driver = None
        
        except Exception as e:
            self.log_message(f"Error: {e}")
        
        finally:
            # Update UI
            self.is_downloading = False
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))

def on_closing(root):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        # Clean up any resources
        root.destroy()
        sys.exit(0)

def main():
    root = tk.Tk()
    app = YandexCrawlerGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    root.mainloop()

if __name__ == "__main__":
    main()
