#!/bin/bash

echo "Yandex Images Downloader"
echo "----------------------"
echo

read -p "Enter search term or URL: " search
read -p "Enter number of images to download (default: 10): " count
read -p "Enter minimum image size (format: WxH, default: 0x0): " size
read -p "Enter output directory (default: downloaded_images): " dir

# Set default values if not provided
count=${count:-10}
size=${size:-0x0}
dir=${dir:-downloaded_images}

echo
echo "Starting download..."
echo

python example_usage.py --search "$search" --count $count --size "$size" --dir "$dir"

echo
echo "Download complete!"
