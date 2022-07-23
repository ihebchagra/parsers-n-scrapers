#!/usr/bin/env python3
import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine
from math import floor
import json

# change niveau to choose which niveau to use
niveau = "dcem3"
database = []
excluded_titles=["AUTO-EVALUATION","TESTS D'EVALUATION","POST-TEST","PRE-TEST","AUTO-ÉVALUATION","TEST D'AUTO EVALUATION","TESTS D'AUTO EVALUATION","TEST D'EVALUATION","QUESTIONS D'AUTO-ÉVALUATION","TESTS D'AUTO-EVALUATION","QUESTIONS D'AUTO-ÉVALUATION","GLOSSAIRE","QUESTIONS D'ÉVALUATION","ANNEXE 1","ANNEXE N 1","TESTS D'AUTOEVALUATION","TESTS D'AUTO-ÉVALUATION","ÉVALUATION FORMATIVE","TESTS D'ÉVALUATION","EVALUATION FORMATIVE","PLAN","ANNEXE","ANNEXES","UNIVERSITE TUNIS EL MANAR FACULTE DE MEDECINE DE TUNIS","TEST D'AUTO-EVALUATION"]
obj = {}

for filename in os.listdir(niveau):
	page=0
	name = filename.replace('.pdf','')
	print("Processing", name)
	infile = os.path.join(niveau, filename)
	obj[name]={}
	for page_layout in extract_pages(infile):
		page+=1
		if page<2:
			continue
		for element in page_layout:
			if isinstance(element, LTTextContainer):
				for text_line in element:
					if isinstance(text_line , LTTextLine):
						for character in text_line:
							if isinstance(character, LTChar):
								if character.size >= 15:
									text=element.get_text().strip().replace('\n',' ').replace('’',"'")
									text=' '.join(text.split())
									if text not in excluded_titles:
										print(page,text)
										obj[name][page]=text
							break
					break

print("writing to {}_titres.js".format(niveau))
json_final = json.dumps(obj, sort_keys=True, indent=0, ensure_ascii=False)
open("{}_titres.js".format(niveau),"w").write("{}_titres={}".format(niveau,json_final))
