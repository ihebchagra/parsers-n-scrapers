# DPM scraper

### How to use this

- visit [https://statmed.org/pages/differential_diagnosis/data/ajax_feature_list.php](https://statmed.org/pages/differential_diagnosis/data/ajax_feature_list.php)
- use featurefixer.js and create features.js by adding "features ="
- visit [https://statmed.org/differential_diagnosis](https://statmed.org/differential_diagnosis)
- open the console
- set up the features array by copying
- set up pathology_obj to be {} at the beginning
- use scraper.js 50 iterations at a time
- at the end of each 50 iterations use the last line to save a checkpoint
- run ratio.py to fix missing sex ratio, having cache.json for this helps. This makes pathologies.json
- run translator.py to translate to french, having dict.json for this helps, this makes database.js which we use for the website and database.json for the next step
- run argumentator.py to get arguments.js for the website
