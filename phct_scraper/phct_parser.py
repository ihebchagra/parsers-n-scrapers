#!/usr/bin/python
from bs4 import BeautifulSoup
import re
import os
import csv # Import the csv module

directory = "pages_downloaded"
all_data = [] # Changed variable name for clarity

print(f"Scanning directory: {directory}")

# Check if directory exists
if not os.path.isdir(directory):
    print(f"Error: Directory '{directory}' not found.")
    exit(1)

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if not os.path.isfile(f):
        continue

    print(f"Processing file: {f}")
    try:
        # Use 'with open' for better file handling
        with open(f, 'r', encoding='utf-8') as html_doc:
            soup = BeautifulSoup(html_doc, 'html.parser')
    except Exception as e:
        print(f"  Error reading or parsing file {f}: {e}")
        continue # Skip to the next file

    for medicament in soup.find_all("div", "modal-content"):
        nom_tag = medicament.find("h4", "modal-title")
        # Check if name tag and its string content exist
        if not nom_tag or not nom_tag.string:
            print(f"  Warning: Could not find name ('h4', 'modal-title') in {filename}. Skipping this entry.")
            continue # Skip this medicament entry
        
        nom = nom_tag.string.strip()
        medicament_data = {"Nom": nom} # Start dictionary for this medicament

        for body in medicament.find_all("div", "modal-body"):
            for entry in body.find_all("div", itemprop=None):
                index = None
                valeur = None

                subtitle_div = entry.find("div", "col-md-6 col-lg-4") # Removed extra comma
                if subtitle_div and subtitle_div.string:
                    index = subtitle_div.string.strip().replace(" :", "")

                value_div = entry.find("div", "col-lg-8")
                if value_div:
                    b_tag = value_div.find("b")
                    if b_tag and b_tag.string:
                        valeur = b_tag.string.strip()

                # Only add if both index (key) and valeur (value) were found
                if index and valeur is not None: # Check value specifically for None
                     # Clean up index name for better CSV header compatibility (optional)
                    # index = index.replace(' ', '_').replace('/', '_').lower() 
                    medicament_data[index] = valeur
                # Optional: Handle cases where only index is found if needed
                # elif index:
                #    medicament_data[index] = "" # Assign empty string if value is missing

        if len(medicament_data) > 1: # Ensure we have more than just the 'Nom'
             all_data.append(medicament_data)
        # else:
        #    print(f"  Warning: No key-value data found for '{nom}' in {filename}.")


# --- CSV Writing Part ---
if not all_data:
    print("No data extracted. CSV file will not be created.")
else:
    csv_filename = "phct.csv"
    print(f"\nWriting data to {csv_filename}")

    # 1. Find all unique field names (column headers) across all dictionaries
    fieldnames_set = set()
    for item in all_data:
        fieldnames_set.update(item.keys())
    
    # Convert set to list and ensure 'Nom' is the first column if present
    fieldnames = sorted(list(fieldnames_set))
    if "Nom" in fieldnames:
        fieldnames.remove("Nom")
        fieldnames.insert(0, "Nom")

    # 2. Write to CSV
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()  # Write the header row
            writer.writerows(all_data) # Write all data rows

        print(f"Successfully wrote {len(all_data)} records to {csv_filename}")
    except Exception as e:
        print(f"Error writing CSV file: {e}")
