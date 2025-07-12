import requests
import re
import os

def clean_url(url):
    """Cleans a URL to be used as a filename."""
    # Remove protocol and www.
    cleaned = re.sub(r'https?://(www\.)?', '', url)
    # Remove paths, queries, etc.
    cleaned = cleaned.split('/')[0]
    return cleaned

def fetch_and_save_robots_txt():
    """Reads URLs from config.txt, fetches robots.txt, and saves them."""
    if not os.path.exists('config.txt'):
        print("config.txt not found.")
        return

    with open('config.txt', 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        try:
            robots_url = f"{url.rstrip('/')}/robots.txt"
            response = requests.get(robots_url)
            response.raise_for_status()  # Raise an exception for bad status codes

            filename_base = clean_url(url)
            filename = f"{filename_base}.robots.txt"

            with open(filename, 'w') as out_file:
                out_file.write(response.text)
            print(f"Successfully fetched and saved {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch robots.txt from {url}: {e}")

if __name__ == "__main__":
    fetch_and_save_robots_txt() 