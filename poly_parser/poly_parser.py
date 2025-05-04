#!/usr/bin/env python3
import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import json
import re

# change niveau to choose which niveau to use
niveau = "pcem1"
database = []
obj = {}

for filename in os.listdir(niveau):
	name = filename.replace('.pdf','')
	print("Processing", name)
	infile = os.path.join(niveau, filename)
	obj[name]=[]
	for page_layout in extract_pages(infile):
		text=''
		for element in page_layout:
		    if isinstance(element, LTTextContainer):
		        text+=element.get_text()
		text=text.strip().replace('\n',' ').replace('\t',' ').replace('  ',' ').replace("’","'").replace("- ","")
		text = re.sub("[^a-zA-Z0-9α-ωΑ-ΩßéêèàïçùœÉÊÈÀÏÇÙŒ\'\-\ ]+", "",text)
		text=' '.join(text.split())
		obj[name].append(text)
print("writing to {}.js".format(niveau))
json_final = json.dumps(obj, sort_keys=False, indent=0, ensure_ascii=False)
open("{}.js".format(niveau),"w").write("{}={}".format(niveau,json_final))
