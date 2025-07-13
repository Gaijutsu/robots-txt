import requests
import re
import os
import glob
from urllib.robotparser import RobotFileParser
from datetime import datetime
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter

ROBOTS_DIR = 'robots_files'

def clean_url(url):
    """Cleans a URL to be used as a filename."""
    # Remove protocol and www.
    cleaned = re.sub(r'https?://(www\.)?', '', url)
    # Remove paths, queries, etc.
    cleaned = cleaned.split('/')[0]
    return cleaned

def fetch_and_save_robots_txt(urls):
    """Reads URLs from config.txt, fetches robots.txt, and saves them."""
    os.makedirs(ROBOTS_DIR, exist_ok=True)
    for url in urls:
        try:
            robots_url = f"{url.rstrip('/')}/robots.txt"
            response = requests.get(robots_url, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes

            filename_base = clean_url(url)
            filename = os.path.join(ROBOTS_DIR, f"{filename_base}.robots.txt")

            with open(filename, 'w', encoding='utf-8') as out_file:
                out_file.write(response.text)
            print(f"Successfully fetched and saved {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch robots.txt from {url}: {e}")

def get_user_agents_from_files(robot_files):
    """Extracts all User-Agents from a list of robots.txt files."""
    user_agents = set(['*'])  # Always include the wildcard
    for file_path in robot_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.strip().lower().startswith('user-agent:'):
                        agent = line.split(':', 1)[1].strip()
                        if agent:
                            user_agents.add(agent)
        except FileNotFoundError:
            print(f"Warning: Could not find {file_path} to extract user agents.")
    return sorted(list(user_agents))

def update_spreadsheet(urls):
    """Creates or updates a spreadsheet with an analysis of robots.txt files."""
    spreadsheet_name = 'robots-analysis.xlsx'
    domains = [clean_url(u) for u in urls]
    domain_to_url = dict(zip(domains, urls))
    robot_files = [os.path.join(ROBOTS_DIR, f"{d}.robots.txt") for d in domains]
    
    if not any(os.path.exists(f) for f in robot_files):
        print("No robots.txt files found to analyze.")
        return

    user_agents = get_user_agents_from_files(robot_files)
    
    data = []
    for ua in user_agents:
        row = {'User-Agent': ua}
        for domain in domains:
            robot_file_path = os.path.join(ROBOTS_DIR, f"{domain}.robots.txt")
            if not os.path.exists(robot_file_path):
                row[domain] = '❓'
                continue

            rp = RobotFileParser()
            # The URL passed to set_url is used as the base for the path in can_fetch
            rp.set_url(f"{domain_to_url[domain].rstrip('/')}/robots.txt")
            with open(robot_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                rp.parse(f.readlines())
            
            # We check if the user agent can fetch the root of the site
            if rp.can_fetch(ua, '/'):
                row[domain] = '✅'
            else:
                row[domain] = '❌'
        data.append(row)

    if not data:
        print("No data to write to spreadsheet.")
        return

    df = pd.DataFrame(data)
    df = df.set_index('User-Agent')
    
    sheet_name = datetime.now().strftime('%Y-%m-%d')

    mode = 'a' if os.path.exists(spreadsheet_name) else 'w'
    with pd.ExcelWriter(
        spreadsheet_name,
        engine='openpyxl',
        mode=mode,
        if_sheet_exists='replace'
    ) as writer:
        df.to_excel(writer, sheet_name=sheet_name)

    # Re-open with openpyxl to apply styles
    book = load_workbook(spreadsheet_name)
    ws = book[sheet_name]
    
    green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
    red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

    for row in ws.iter_rows(min_row=2, min_col=2):  # Skip header and index column
        for cell in row:
            if cell.value == '✅':
                cell.fill = green_fill
            elif cell.value == '❌':
                cell.fill = red_fill

    # Auto-fit columns
    for col in ws.columns:
        max_length = 0
        column = get_column_letter(col[0].column)
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width
        
    book.save(spreadsheet_name)
    print(f"Spreadsheet '{spreadsheet_name}' updated with new sheet '{sheet_name}'.")

def main():
    """Main function to run the script."""
    config_file = 'config.txt'
    if not os.path.exists(config_file):
        print(f"{config_file} not found.")
        return

    with open(config_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    fetch_and_save_robots_txt(urls)
    update_spreadsheet(urls)

if __name__ == "__main__":
    main() 