# Yandex Images Crawler Usage Guide

This guide explains how to use the Yandex Images Crawler to download a limited number of images from Yandex search results.

## Quick Start

For the easiest way to get started:

1. **GUI Application**: Run `python yandex_crawler_gui.py` for a user-friendly graphical interface
2. **Windows users**: Run `download_images.bat` and follow the prompts
3. **Linux/Mac users**: Run `bash download_images.sh` and follow the prompts
4. **Ready-to-run example**: Run `python download_cat_images.py` to download 10 cat images
5. **Customizable script**: Edit the variables in `custom_download.py` and run it with `python custom_download.py`
6. **No ChromeDriver hassle**: Run `python auto_webdriver_example.py` to automatically handle ChromeDriver installation
7. **Safe crawler**: Run `python safe_crawler.py --search "your search"` for a version with better error handling

## Prerequisites

1. Python 3.6 or higher
2. Chrome browser installed
3. ChromeDriver installed (for Selenium)

## Installation

### Easy Installation

Run the installation script to automatically install all dependencies:

```bash
python install_dependencies.py
```

This script will:
1. Check if you have Python 3.6 or higher
2. Check if Chrome is installed
3. Install the Yandex Images Crawler package and other dependencies
4. Help you set up ChromeDriver

### Manual Installation

If you prefer to install manually:

```bash
pip install yandex-images-crawler selenium webdriver-manager
```

You'll also need:
1. Chrome browser installed
2. ChromeDriver installed (or use webdriver-manager to manage it automatically)

## Basic Usage

You can use the provided `example_usage.py` script to download images:

```bash
python example_usage.py --search "cats" --count 20 --dir "cat_images"
```

This will download 20 cat images to the "cat_images" directory.

### Command-line Arguments

- `--search`: Search term or full Yandex Images search URL (required)
- `--count`: Number of images to download (default: 10)
- `--size`: Minimum image size in format WxH (e.g., 800x600). Default: no size limit (0x0)
- `--dir`: Directory to save downloaded images (default: "downloaded_images")
- `--headless`: Run in headless mode (no browser UI)

### Examples

1. Download 5 dog images:
   ```bash
   python example_usage.py --search "dogs" --count 5
   ```

2. Download 15 landscape images with minimum size 1920x1080:
   ```bash
   python example_usage.py --search "landscape photography" --count 15 --size "1920x1080"
   ```

3. Use a specific Yandex search URL (with filters already applied):
   ```bash
   python example_usage.py --search "https://yandex.com/images/search?text=mountain%20view&isize=large" --count 10
   ```

4. Run in headless mode (no browser windows):
   ```bash
   python example_usage.py --search "flowers" --count 10 --headless
   ```

## Advanced Usage

### Command Line Usage

For more advanced options, you can use the Yandex Images Crawler directly:

```bash
yandex-images-crawler --links "https://yandex.com/images/search?text=cats" --count 20 --size "800x600" --dir "cat_images"
```

See the [official documentation](https://github.com/suborofu/yandex-images-crawler) for more advanced options.

### Direct Python Integration

If you want to integrate the crawler into your own Python code, you can use the `direct_usage_example.py` script as a reference:

```python
from yandex_images_crawler.download import download

# Download 5 cat images
download(
    links=["https://yandex.com/images/search?text=cats"],
    image_size=(0, 0),  # No minimum size
    image_count=5,
    image_dir="cat_images",
    skip_files=frozenset(),
    loaders_per_link=1,
    headless_mode=False
)
```

## GUI Application

The GUI application provides a user-friendly interface for downloading images from Yandex. It includes:

- Easy-to-use form for entering search terms and settings
- Real-time status updates and progress tracking
- Ability to stop downloads at any time
- Automatic ChromeDriver installation
- Error handling and timeout features

To run the GUI application:

```bash
python yandex_crawler_gui.py
```

## Troubleshooting

1. **Browser windows not opening**: Make sure Chrome and ChromeDriver are installed and up to date. For the easiest setup, use the GUI application or the `auto_webdriver_example.py` script which automatically handles ChromeDriver installation.

2. **No images downloaded**: Check your search term or URL. Some searches may not return many results.

3. **Slow downloads**: Try using the headless mode option for faster downloads, or increase the number of loaders with the `--loaders-per-link` option when using the crawler directly.

4. **Error messages**: If you see Selenium-related errors, make sure your ChromeDriver version matches your Chrome browser version. The GUI application and `auto_webdriver_example.py` script can help avoid these issues by automatically managing ChromeDriver.

5. **Endless error loops**: If you encounter endless error messages about not being able to move to the next image, use the `safe_crawler.py` script or the GUI application, which include better error handling and will automatically stop after a certain number of consecutive errors.
