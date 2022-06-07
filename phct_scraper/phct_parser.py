#!/usr/bin/python
from bs4 import BeautifulSoup
import re
import os
import json

directory="pages_downloaded"
json_output=[]
for filename in os.listdir(directory):
	f = os.path.join(directory, filename)
	if not os.path.isfile(f):
		continue
	html_doc = open(f)
	soup = BeautifulSoup(html_doc, 'html.parser')
	html_doc.close()
	for medicament in soup.find_all("div", "modal-content"):
		nom = medicament.find("h4","modal-title").string
		object = {"Nom" : nom}
		for body in medicament.find_all("div", "modal-body"):
			for entry in body.find_all("div", itemprop=None):
				subtitle = entry.find("div","col-md-6", "col-lg-4")
				if subtitle != None:
					index=subtitle.string.replace(" :","")
				value = entry.find("div", "col-lg-8")
				if value != None:
					valeur=value.find("b").string
				object.update({index : valeur})
		json_output.append(object)
	print(f)
print("writing to medicaments.json")
json_final = json.dumps(json_output, sort_keys=False, indent=4, ensure_ascii=False)
open("medicaments.json","w").write(json_final)
