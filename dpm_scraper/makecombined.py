import pandas as pd
import numpy as np
import logging
import re
import sqlite3 # Import the SQLite library

# --- Configuration ---
CNAM_FILE = 'cnam.csv'
DPM_FILE = 'dpm.json'
PHCT_FILE = 'phct.csv'
OUTPUT_CSV_FILE = 'medicaments_final.csv'
SQLITE_DB_FILE = 'medicaments_fts.db'
FTS_TABLE_NAME = 'medicaments_fts'
LOG_FILE = 'merge_log.log'

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w'),
        logging.StreamHandler()
    ]
)

logging.info("Starting the consolidated merge and SQLite FTS5 export process...")

# --- Helper functions ---
def clean_amm(amm_string):
    if pd.isna(amm_string): return None
    cleaned = str(amm_string).strip().replace('*', '')
    cleaned = re.sub(r'[A-Za-z]$', '', cleaned)
    return cleaned

def clean_dci(dci_string):
    if pd.isna(dci_string): return None
    return str(dci_string).strip().upper()

# --- Load Data ---
try:
    logging.info(f"Loading {CNAM_FILE}...")
    df_cnam = pd.read_csv(CNAM_FILE, sep=',', decimal=',')
    logging.info(f"Loaded {len(df_cnam)} rows from {CNAM_FILE}.")
    df_cnam.columns = df_cnam.columns.str.strip()

    logging.info(f"Loading {DPM_FILE}...")
    df_dpm = pd.read_json(DPM_FILE)
    logging.info(f"Loaded {len(df_dpm)} rows from {DPM_FILE}.")
    # *** UPDATED DPM COLUMN MAPPING ***
    dpm_column_mapping = {
        "Spécialité": "Nom_dpm_source",
        "Dosage": "Dosage_dpm_source", # Added Dosage
        "Forme": "Forme_dpm_source",
        "Présentation": "Présentation_dpm_source",
        "Conditionnement primaire": "Conditionnement_dpm_source",
        "Spécification": "Spécification_dpm_source",
        "DCI": "DCI_dpm_source",
        "Classement VEIC": "VEIC_dpm_source",
        "Classe Thérapeutique": "Classe_dpm_source",
        "Sous Classe": "Sous_Classe_dpm_source",
        "Laboratoire": "Laboratoire_dpm_source",
        "Tableau": "Tableau_dpm_source",
        "Durée de conservation": "Duree_Conservation_dpm_source",
        "Indication": "Indications_dpm_source",
        "AMM": "AMM_dpm_source",
        "Date AMM": "Date_AMM_dpm_source",
        "rcp": "RCP_dpm_source",       # Added RCP link
        "notice": "Notice_dpm_source"  # Added Notice link
        # Ignore 'id', 'is_sup'
    }
    # Keep only the columns we have mapped
    mapped_dpm_cols = list(dpm_column_mapping.keys())
    df_dpm_filtered = df_dpm[[col for col in mapped_dpm_cols if col in df_dpm.columns]].copy()
    df_dpm = df_dpm_filtered.rename(columns=dpm_column_mapping)

    logging.info("Renamed DPM columns with '_dpm_source' suffix.")
    df_dpm.columns = df_dpm.columns.str.strip()

    logging.info(f"Loading {PHCT_FILE}...")
    df_phct = pd.read_csv(PHCT_FILE, sep=',')
    logging.info(f"Loaded {len(df_phct)} rows from {PHCT_FILE}.")
    df_phct.columns = df_phct.columns.str.strip()
    df_phct.rename(columns={'AMM': 'AMM_phct_source'}, inplace=True)

except FileNotFoundError as e:
    logging.error(f"Error loading file: {e}. Please ensure all input files are present.")
    exit()
except ValueError as e:
    logging.error(f"Error parsing JSON file {DPM_FILE}: {e}. Check JSON format.")
    exit()
except Exception as e:
    logging.error(f"An error occurred during file loading: {e}")
    exit()

# --- Prepare Keys and Clean Data ---
logging.info("Preparing join keys and cleaning data...")
df_cnam['CODE_PCT_str'] = df_cnam['CODE_PCT'].astype(str).str.strip()
df_cnam['DCI_cleaned'] = df_cnam['DCI'].apply(clean_dci)
df_cnam.rename(columns={'NOM_COMMERCIAL': 'Nom_cnam_source', 'DCI': 'DCI_cnam_source'}, inplace=True)

df_phct['Code Produit_str'] = df_phct['Code Produit'].astype(str).str.strip()
df_phct['AMM_cleaned'] = df_phct['AMM_phct_source'].apply(clean_amm)
df_phct['DCI_cleaned'] = df_phct['DCI1'].apply(clean_dci)

df_dpm['AMM_cleaned'] = df_dpm['AMM_dpm_source'].apply(clean_amm)
df_dpm['DCI_cleaned'] = df_dpm['DCI_dpm_source'].apply(clean_dci)

# --- Handle Duplicates in PHCT ---
logging.info("Handling duplicates in PHCT...")
phct_mapping = df_phct[['Code Produit_str', 'AMM_cleaned', 'AMM_phct_source', 'DCI_cleaned']].copy()
phct_mapping.dropna(subset=['Code Produit_str'], inplace=True)
phct_mapping.sort_values(by='AMM_cleaned', na_position='last', inplace=True)
initial_rows = len(phct_mapping)
phct_mapping.drop_duplicates(subset=['Code Produit_str'], keep='first', inplace=True)
dropped_count = initial_rows - len(phct_mapping)
if dropped_count > 0:
    logging.warning(f"Dropped {dropped_count} duplicate mappings in PHCT based on 'Code Produit'. Prioritized entries with an AMM.")
phct_amm_mapping = phct_mapping[['Code Produit_str', 'AMM_cleaned', 'AMM_phct_source']].dropna(subset=['AMM_cleaned'])

# --- Merge 1: CNAM <-> PHCT ---
logging.info("Merging CNAM with PHCT mapping...")
df_merged1 = pd.merge(df_cnam, phct_amm_mapping, left_on='CODE_PCT_str', right_on='Code Produit_str', how='left')
logging.info(f"Merge 1 (CNAM-PHCT) result: {len(df_merged1)} rows.")
cnam_no_amm_match_count = df_merged1['AMM_cleaned'].isnull().sum()
if cnam_no_amm_match_count > 0:
    logging.warning(f"{cnam_no_amm_match_count} rows from CNAM did not find a corresponding 'Code Produit' with an AMM in PHCT.")

# --- Prepare DPM Data (Fallback Map & Unique AMM) ---
logging.info("Creating DCI fallback map and preparing DPM for merges...")
# Add new DPM cols to fallback map if needed (likely not, but good practice)
fallback_cols = ['DCI_cleaned', 'Indications_dpm_source', 'Classe_dpm_source',
                 'Sous_Classe_dpm_source', 'Laboratoire_dpm_source', 'Dosage_dpm_source']
fallback_cols = [col for col in fallback_cols if col in df_dpm.columns]
dpm_fallback_map_df = df_dpm[fallback_cols].copy()
dpm_fallback_map_df.dropna(subset=['DCI_cleaned', 'Indications_dpm_source'], inplace=True) # Still based on DCI/Indications
dpm_fallback_map_df.drop_duplicates(subset=['DCI_cleaned'], keep='first', inplace=True)
dci_fallback_map = dpm_fallback_map_df.set_index('DCI_cleaned').to_dict(orient='index')
logging.info(f"Created fallback map for {len(dci_fallback_map)} unique DCIs.")

initial_dpm_rows = len(df_dpm)
if 'AMM_cleaned' not in df_dpm.columns:
     logging.error("Critical error: 'AMM_cleaned' column not found in DPM DataFrame.")
     exit()
df_dpm.dropna(subset=['AMM_cleaned'], inplace=True)
# Ensure all _dpm_source columns are included in the merge selection
dpm_merge_cols = ['AMM_cleaned', 'DCI_cleaned'] + [col for col in df_dpm.columns if col.endswith('_dpm_source')]
dpm_merge_cols = [col for col in dpm_merge_cols if col in df_dpm.columns] # Ensure existence
df_dpm_unique_amm = df_dpm[dpm_merge_cols].drop_duplicates(subset=['AMM_cleaned'], keep='first').copy()
dropped_dpm_count = (initial_dpm_rows - len(df_dpm)) + (len(df_dpm) - len(df_dpm_unique_amm))
if dropped_dpm_count > 0:
    logging.warning(f"Dropped {dropped_dpm_count} duplicate or NaN-key rows in DPM based on cleaned 'AMM'. Kept the first DPM entry.")


# --- Merge 2: (CNAM + PHCT) <-> DPM ---
logging.info("Merging result with DPM data (on AMM)...")
df_final = pd.merge(df_merged1, df_dpm_unique_amm, on='AMM_cleaned', how='left')
logging.info(f"Merge 2 (AMM-based) result: {len(df_final)} rows.")

# --- Identify DPM Indicator Column ---
dpm_indicator_col = 'Nom_dpm_source' if 'Nom_dpm_source' in df_final.columns else None
if not dpm_indicator_col:
     dpm_source_cols_present = [col for col in df_final.columns if col.endswith('_dpm_source')]
     if dpm_source_cols_present:
         dpm_indicator_col = dpm_source_cols_present[0]

# --- Apply Fallback ---
logging.info("Checking AMM merge success and applying DCI fallback...")
fallback_applied_count = 0
if not dpm_indicator_col:
    logging.warning("Could not determine DPM indicator column. Skipping AMM match check and fallback.")
else:
    logging.info(f"Using indicator column '{dpm_indicator_col}' to check DPM merge success.")
    amm_merge_failed_mask = df_final['AMM_cleaned'].notna() & df_final[dpm_indicator_col].isnull()
    dpm_amm_match_failed_count = amm_merge_failed_mask.sum()
    if dpm_amm_match_failed_count > 0:
        logging.warning(f"{dpm_amm_match_failed_count} rows had AMM link but failed AMM merge. Attempting DCI fallback.")
        cnam_dci_col = 'DCI_cleaned_cnam' if 'DCI_cleaned_cnam' in df_final.columns else 'DCI_cleaned'
        if cnam_dci_col not in df_final.columns:
             logging.warning(f"CNAM DCI column ('{cnam_dci_col}') not found for fallback.")
        else:
            # Add new cols to fallback map if needed (e.g., Dosage)
            fallback_target_cols_map = {
                'Indications_dpm_source': 'Indications_dpm_source', 'Classe_dpm_source': 'Classe_dpm_source',
                'Sous_Classe_dpm_source': 'Sous_Classe_dpm_source', 'Laboratoire_dpm_source': 'Laboratoire_dpm_source',
                'Dosage_dpm_source': 'Dosage_dpm_source' # Add Dosage to fallback
            }
            rows_filled_by_fallback = 0
            for source_col, target_col in fallback_target_cols_map.items():
                # Check if target col exists and source col exists in fallback map data structure
                if target_col in df_final.columns and source_col in dci_fallback_map[next(iter(dci_fallback_map))]:
                    fallback_values = df_final.loc[amm_merge_failed_mask, cnam_dci_col].map(lambda dci: dci_fallback_map.get(dci, {}).get(source_col))
                    df_final.loc[amm_merge_failed_mask, target_col] = df_final.loc[amm_merge_failed_mask, target_col].fillna(fallback_values)
                    if target_col == fallback_target_cols_map['Indications_dpm_source']:
                         rows_filled_by_fallback = fallback_values.notna().sum()
            if rows_filled_by_fallback > 0:
                 logging.info(f"Successfully applied DCI fallback for {rows_filled_by_fallback} rows.")
                 fallback_applied_count = rows_filled_by_fallback
            else:
                 logging.warning("DCI fallback attempted, but no matching DCIs found or no rows needed filling.")


# --- Identify and Prepare Skipped DPM Data ---
logging.info("Identifying DPM entries not linked to CNAM...")
successfully_merged_amms_set = set()
if dpm_indicator_col:
    successfully_merged_amms = df_final.loc[df_final['AMM_cleaned'].notna() & df_final[dpm_indicator_col].notna(), 'AMM_cleaned'].unique()
    successfully_merged_amms_set = set(filter(None, successfully_merged_amms))
original_dpm_amms_set = set(filter(None, df_dpm_unique_amm['AMM_cleaned'].unique()))
skipped_amms = original_dpm_amms_set - successfully_merged_amms_set
logging.info(f"Found {len(skipped_amms)} unique AMMs from DPM not successfully linked.")

skipped_dpm_rows_to_add = pd.DataFrame()
if skipped_amms:
    # Use df_dpm_unique_amm which contains all the needed _dpm_source columns
    skipped_dpm_rows = df_dpm_unique_amm[df_dpm_unique_amm['AMM_cleaned'].isin(skipped_amms)].copy()
    skipped_dpm_rows.dropna(subset=['DCI_cleaned'], inplace=True)
    logging.info(f"Found {len(skipped_dpm_rows)} skipped DPM entries with a DCI to potentially add.")
    if not skipped_dpm_rows.empty:
        skipped_dpm_rows_to_add = skipped_dpm_rows

# --- CONSOLIDATE DATA into DataFrame ---
logging.info("Consolidating data into final columns...")
df_combined = pd.concat([df_final, skipped_dpm_rows_to_add], ignore_index=True, sort=False)
logging.info(f"Temporarily combined CNAM-based ({len(df_final)} rows) and skipped DPM ({len(skipped_dpm_rows_to_add)} rows). Total: {len(df_combined)} rows.")

# *** UPDATED CONSOLIDATION ***
final_cols = {}
final_cols['CODE_PCT'] = df_combined.get('CODE_PCT')
final_cols['PRIX_PUBLIC'] = df_combined.get('PRIX_PUBLIC')
final_cols['TARIF_REFERENCE'] = df_combined.get('TARIF_REFERENCE')
final_cols['CATEGORIE'] = df_combined.get('CATEGORIE')
final_cols['AP'] = df_combined.get('AP')
final_cols['Nom_Commercial'] = df_combined.get('Nom_cnam_source').fillna(df_combined.get('Nom_dpm_source'))
final_cols['Dosage'] = df_combined.get('Dosage_dpm_source') # Added Dosage
final_cols['DCI'] = df_combined.get('DCI_dpm_source').fillna(df_combined.get('DCI_cnam_source'))
final_cols['AMM'] = df_combined.get('AMM_dpm_source').fillna(df_combined.get('AMM_phct_source'))
final_cols['Laboratoire'] = df_combined.get('Laboratoire_dpm_source')
final_cols['Classe_Therapeutique'] = df_combined.get('Classe_dpm_source')
final_cols['Sous_Classe_Therapeutique'] = df_combined.get('Sous_Classe_dpm_source')
final_cols['Indications'] = df_combined.get('Indications_dpm_source')
final_cols['Forme'] = df_combined.get('Forme_dpm_source')
final_cols['Presentation'] = df_combined.get('Présentation_dpm_source') # Corrected typo if any
final_cols['Date_AMM'] = df_combined.get('Date_AMM_dpm_source')
final_cols['VEIC'] = df_combined.get('VEIC_dpm_source')
final_cols['Tableau'] = df_combined.get('Tableau_dpm_source')
final_cols['Duree_Conservation'] = df_combined.get('Duree_Conservation_dpm_source')
final_cols['Conditionnement_Primaire'] = df_combined.get('Conditionnement_dpm_source')
final_cols['Specification_Conditionnement'] = df_combined.get('Spécification_dpm_source') # Corrected typo if any
final_cols['RCP_Link'] = df_combined.get('RCP_dpm_source') # Added RCP
final_cols['Notice_Link'] = df_combined.get('Notice_dpm_source') # Added Notice

df_final_consolidated = pd.DataFrame(final_cols)

# --- Final Cleanup ---
df_final_consolidated.dropna(subset=['Nom_Commercial', 'DCI'], how='all', inplace=True)
logging.info(f"Removed rows missing both Nom_Commercial and DCI. Rows remaining: {len(df_final_consolidated)}")
df_final_consolidated.dropna(axis=1, how='all', inplace=True)

# --- Reorder Columns ---
# *** UPDATED ORDERING ***
desired_order = [
    'CODE_PCT', 'Nom_Commercial', 'Dosage', 'DCI', 'AMM', 'Laboratoire', # Added Dosage
    'PRIX_PUBLIC', 'TARIF_REFERENCE', 'CATEGORIE', 'AP',
    'Indications', 'Classe_Therapeutique', 'Sous_Classe_Therapeutique',
    'Forme', 'Presentation', 'Date_AMM', 'VEIC', 'Tableau',
    'Duree_Conservation', 'Conditionnement_Primaire', 'Specification_Conditionnement',
    'RCP_Link', 'Notice_Link' # Added Links
]
final_col_order = [col for col in desired_order if col in df_final_consolidated.columns]
other_cols = [col for col in df_final_consolidated.columns if col not in final_col_order]
final_col_order.extend(other_cols)
try:
    df_final_consolidated = df_final_consolidated[final_col_order]
    logging.info("Reordered columns in the final DataFrame.")
except KeyError as e:
    logging.warning(f"Could not reorder columns due to missing key: {e}. Keeping current order.")

# --- Save Result to CSV ---
logging.info(f"Saving consolidated data to {OUTPUT_CSV_FILE}...")
try:
    df_final_consolidated.to_csv(OUTPUT_CSV_FILE, index=False, sep=';', decimal=',')
    logging.info(f"Successfully saved consolidated data to CSV with {len(df_final_consolidated)} rows.")
except Exception as e:
    logging.error(f"Error saving CSV output file: {e}")


# --- Save to SQLite FTS5 Table ---
logging.info(f"Preparing to save data to SQLite FTS5 table: {SQLITE_DB_FILE}")

# *** UPDATED FTS DEFINITION ***
fts_indexed_columns = [
    'Nom_Commercial', 'DCI', 'Indications', 'Laboratoire',
    'Classe_Therapeutique', 'Sous_Classe_Therapeutique',
    'Forme', 'Presentation', 'Dosage' # Added Dosage to FTS index
]

all_columns = df_final_consolidated.columns.tolist()

# RCP and Notice links are usually not useful for FTS, keep them unindexed
unindexed_columns = [col for col in all_columns if col not in fts_indexed_columns]

quoted_all_columns = [f'"{col}"' for col in all_columns]
quoted_fts_indexed_columns = [f'"{col}"' for col in fts_indexed_columns if col in all_columns]
quoted_unindexed_columns = [f'"{col}" UNINDEXED' for col in unindexed_columns if col in all_columns]

fts_cols_definition = quoted_fts_indexed_columns + quoted_unindexed_columns
create_fts_table_sql = f"""
CREATE VIRTUAL TABLE "{FTS_TABLE_NAME}" USING fts5(
    {', '.join(fts_cols_definition)},
    tokenize='unicode61'
);
"""
drop_fts_table_sql = f'DROP TABLE IF EXISTS "{FTS_TABLE_NAME}";'

insert_sql = f"""
INSERT INTO "{FTS_TABLE_NAME}" ({', '.join(quoted_all_columns)})
VALUES ({', '.join(['?'] * len(all_columns))})
"""

data_to_insert = [
    tuple(row.where(pd.notna(row), None))
    for _, row in df_final_consolidated.iterrows()
]

conn = None
try:
    logging.info(f"Connecting to SQLite database: {SQLITE_DB_FILE}")
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cursor = conn.cursor()

    logging.info(f"Dropping existing table '{FTS_TABLE_NAME}' if it exists...")
    cursor.execute(drop_fts_table_sql)

    logging.info(f"Creating FTS5 table '{FTS_TABLE_NAME}'...")
    cursor.execute(create_fts_table_sql)
    logging.info("FTS5 table created successfully.")

    logging.info(f"Inserting {len(data_to_insert)} rows into table '{FTS_TABLE_NAME}'...")
    cursor.executemany(insert_sql, data_to_insert)
    logging.info("Data insertion complete.")

    conn.commit()
    logging.info("Data committed to SQLite database.")

except sqlite3.Error as e:
    logging.error(f"SQLite error occurred: {e}")
    if conn:
        logging.warning("Rolling back transaction due to error.")
        conn.rollback()
except Exception as e:
    logging.error(f"An unexpected error occurred during SQLite operations: {e}")
    if conn:
        conn.rollback()
finally:
    if conn:
        conn.close()
        logging.info("SQLite connection closed.")


logging.info("Process finished.")
