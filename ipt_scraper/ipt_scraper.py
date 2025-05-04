import re
import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import os.path

def create_database():
    """Create SQLite database with FTS5 table for the medical test data"""
    conn = sqlite3.connect('prelevements.db')
    cursor = conn.cursor()
    
    # Create table using FTS5 for full-text search
    cursor.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS prelevements USING fts5(
        title,
        price,
        delay,
        laboratory,
        specimens,
        technique,
        code_ipt
    )
    ''')
    
    conn.commit()
    return conn, cursor

def extract_data(html_content):
    """Extract relevant data from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the main content div
    content_div = soup.find('div', id='imprimercontenue')
    if not content_div:
        return None
    
    # Extract title
    title_element = content_div.find('h3')
    title = title_element.get_text().strip() if title_element else "Unknown Title"
    
    # Extract price
    price_element = content_div.find('div', class_='tpast', string=lambda text: text and 'Prix' in text)
    price = price_element.get_text().replace('Prix :', '').strip() if price_element else "Unknown Price"
    
    # Extract delay
    delay_element = content_div.find('div', class_='tpast', string=lambda text: text and 'Délai' in text)
    delay = delay_element.get_text().replace('Délai Résultat :', '').strip() if delay_element else "Unknown Delay"
    
    # Extract laboratory
    lab_section = None
    for h4 in content_div.find_all('h4'):
        if 'Laboratoire' in h4.get_text():
            lab_section = h4
            break
    
    laboratory = ""
    if lab_section and lab_section.find_next('h5'):
        laboratory = lab_section.find_next('h5').get_text().strip().replace('• ', '')
    
    # Extract specimens
    specimens_text = ""
    specimens_section = content_div.find('h4', string=lambda text: text and 'Spécimens' in text)
    if specimens_section:
        specimens_element = specimens_section.find_next('ul')
        if specimens_element:
            specimens_text = specimens_element.get_text().strip()
    
    # Extract technique
    technique = ""
    technique_section = content_div.find('h4', string=lambda text: text and 'Technique' in text)
    if technique_section and technique_section.find_next('h5'):
        technique = technique_section.find_next('h5').get_text().strip().replace('• ', '')
    
    # Extract code IPT
    code_ipt = ""
    code_element = content_div.find('div', class_='tpast', string=lambda text: text and 'Code IPT' in text)
    if code_element:
        code_ipt = code_element.get_text().replace('Code IPT :', '').strip()
    
    return {
        'title': title,
        'price': price,
        'delay': delay,
        'laboratory': laboratory,
        'specimens': specimens_text,
        'technique': technique,
        'code_ipt': code_ipt
    }

def main():
    # Check if pasteur.txt exists
    if not os.path.isfile('pasteur.txt'):
        print("Error: pasteur.txt file not found")
        return
    
    # Create or connect to database
    conn, cursor = create_database()
    
    # Read URLs from file
    with open('pasteur.txt', 'r') as file:
        urls = [line.strip() for line in file if line.strip()]
    
    total_urls = len(urls)
    processed = 0
    successful = 0
    
    # Process each URL
    for url in urls:
        processed += 1
        try:
            print(f"Processing {processed}/{total_urls}: {url}")
            
            # Download HTML content
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # Raise exception for bad status codes
            
            # Extract data
            data = extract_data(response.text)
            
            if data:
                # Insert data into database
                cursor.execute('''
                INSERT INTO prelevements (title, price, delay, laboratory, specimens, technique, code_ipt)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['title'],
                    data['price'], 
                    data['delay'],
                    data['laboratory'],
                    data['specimens'],
                    data['technique'],
                    data['code_ipt']
                ))
                conn.commit()
                successful += 1
                print(f"Added: {data['title']}")
            else:
                print(f"Failed to extract data from {url}")
                
            # Be nice to the server
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
    
    print(f"\nProcessing complete: {successful} out of {total_urls} URLs were successfully processed.")
    conn.close()

if __name__ == "__main__":
    main()
