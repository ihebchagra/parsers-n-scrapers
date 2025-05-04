# DPM scraper

### dependencies

- Beautiful Soup 4

### How to use this

- open these three links and save them as dpm.html, dpmsup.html and dpmsus.html:
  - http://www.dpm.tn/dpm_pharm/medicament/listmedicparnomspec.php
  - http://www.dpm.tn/dpm_pharm/medicament/listmedicparnomspecsup.php
  - http://www.dpm.tn/dpm_pharm/medicament/listmedicparnomspecsuspendues.php
- run dpm_scraper.py
- run dpm_parser.py
- you will have a ready database in medicaments.json and autocomplete.js

# NEW SYSTEM:

- get cnam.csv from the "Liste des médicaments couverts par le régime de base classés en VEI (mise à jour le : 18/03/2025)" at https://www.cnam.nat.tn/espace_ps.jsp
- get dpm.csv from the "Liste complète des AMMs format Excel [Télécharger]" at http://www.dpm.tn/medicament/humain/liste-des-medicaments
- get phct.csv from ../phct_scraper/ script
