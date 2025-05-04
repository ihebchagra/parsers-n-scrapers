#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import re
import os
import time  # Import the time module for delays

# --- Configuration ---
BASE_URL = 'http://www.phct.com.tn/index.php/medicaments-humain'
PARAMS = {
    'resetfilters': '0',
    'clearordering': '0',
    'clearfilters': '0',
    'limit22': '100', # Items per page
    'limitstart22': '0' # Initial start index
}
OUTPUT_DIR = "pages_downloaded"
MAX_RETRIES = 3       # Number of times to retry a failed request
RETRY_DELAY = 5       # Seconds to wait between retries
PAGE_DELAY = 1        # Seconds to wait between downloading different pages (be polite!)
REQUEST_TIMEOUT = 30  # Seconds to wait for the server to respond/send data
HEADERS = {           # Use a realistic User-Agent
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
# --- End Configuration ---

# Use a Session object for potential connection reuse and default headers
session = requests.Session()
session.headers.update(HEADERS)

# --- Function to get the total number of pages ---
def get_total_pages(url, params):
    print("Checking number of pages...")
    try:
        r = session.get(url, params=params, allow_redirects=True, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        soup = BeautifulSoup(r.content, 'html.parser')

        # Fix DeprecationWarning: Use string= instead of text=
        # Make regex more specific to avoid potential mismatches
        page_element = soup.find("small", string=re.compile(r"Page\s+1\s+sur\s+\d+"))

        if not page_element or not page_element.string:
             print("Error: Could not find the pagination element on the page.")
             # print(r.text) # Uncomment to print HTML for debugging
             return None

        # Extract the number more robustly
        match = re.search(r"sur\s+(\d+)", page_element.string.strip())
        if not match:
            print(f"Error: Could not parse total pages from string: '{page_element.string.strip()}'")
            return None

        pages = int(match.group(1))
        print(f"{pages} pages detected")
        return pages

    except requests.exceptions.RequestException as e:
        print(f"Error fetching initial page to determine page count: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while getting page count: {e}")
        return None

# --- Main Script ---

# 1. Get total pages
total_pages = get_total_pages(BASE_URL, PARAMS)
if total_pages is None:
    print("Could not determine the number of pages. Exiting.")
    exit(1)

# 2. Create output directory
try:
    # Use makedirs with exist_ok=True to avoid error if dir already exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory '{OUTPUT_DIR}' ensured.")
except OSError as e:
    print(f"Error creating directory {OUTPUT_DIR}: {e}")
    exit(1) # Can't proceed without output directory

# 3. Loop through pages and download with retries
for i in range(total_pages):
    page_num = i + 1
    start_index = i * int(PARAMS['limit22']) # Calculate start index based on items per page
    current_params = PARAMS.copy()
    current_params['limitstart22'] = str(start_index)
    
    print(f"Attempting download for page {page_num} (start index {start_index})...")
    
    success = False
    for attempt in range(MAX_RETRIES):
        try:
            # Make the request for the current page
            r = session.get(BASE_URL, params=current_params, allow_redirects=True, timeout=REQUEST_TIMEOUT)
            r.raise_for_status() # Check for HTTP errors

            # Save the content if successful
            file_path = os.path.join(OUTPUT_DIR, f"{i}.html") # Use os.path.join for cross-platform compatibility
            with open(file_path, "wb") as f:
                f.write(r.content) # Accessing .content can trigger the ChunkedEncodingError if download fails midway

            print(f"Successfully downloaded page {page_num} to {file_path}")
            success = True
            break # Exit retry loop on success

        except requests.exceptions.RequestException as e: # Catch RequestException (includes ChunkedEncodingError, ConnectionError, Timeout, etc.)
            print(f"Error on page {page_num}, attempt {attempt + 1}/{MAX_RETRIES}: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Failed to download page {page_num} after {MAX_RETRIES} attempts. Skipping.")
        except Exception as e:
             print(f"An unexpected error occurred on page {page_num}, attempt {attempt + 1}/{MAX_RETRIES}: {e}")
             # Decide if you want to retry for unexpected errors too
             if attempt < MAX_RETRIES - 1:
                 print(f"Retrying in {RETRY_DELAY} seconds...")
                 time.sleep(RETRY_DELAY)
             else:
                print(f"Failed to download page {page_num} due to unexpected error after {MAX_RETRIES} attempts. Skipping.")

    # Be polite: wait a bit before requesting the next page
    if i < total_pages - 1: # No need to sleep after the last page
        print(f"Waiting {PAGE_DELAY} second(s)...")
        time.sleep(PAGE_DELAY)

print("\nFinished downloading.")
