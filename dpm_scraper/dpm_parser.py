#!/usr/bin/python

from bs4 import BeautifulSoup
import re
import os
import json

html_doc=open("dpm.html")
print("loading dpm.html file")
bigsoup=BeautifulSoup(html_doc, 'html.parser')
html_doc.close()
autocomplete = []

directory="pages_downloaded"
json_output=[]
length=len(os.listdir(directory))
i=0
for filename in os.listdir(directory):
	i=i+1
	print("fetching médicament ",i,"/",length)
	f = os.path.join(directory, filename)
	if not os.path.isfile(f):
		continue
	fiche = open(f)
	soup = BeautifulSoup(fiche, 'html.parser')
	fiche.close()
	object = {}
	for entry in soup.find_all("tr"):
		if entry.find("b") is None:
			continue
		if entry.find_all('td')[1].font.string is None:
			continue
		if next(entry.b.strings) == 'AMM :':
			amm=entry.find_all('td')[1].font.string
		index=next(entry.b.strings).replace(" :","").replace(" ","")
		valeur=entry.find_all('td')[1].font.string.replace("\n"," ")
		if index in ['DCI','Spécialité']:
			if valeur not in autocomplete:
				autocomplete.append(valeur)
		object.update({index : valeur})
	bigparent=bigsoup.find(string=re.compile(amm)).parent.parent
	if bigparent.find('a',href=re.compile("rcp.pdf")) is not None:
		valeur=bigparent.find('a',href=re.compile("rcp.pdf"))['href'].replace('../..','http://www.dpm.tn')
		index='rcp'
		object.update({index : valeur})
	if bigparent.find('a',href=re.compile("notice.pdf")) is not None:
		valeur=bigparent.find('a',href=re.compile("notice.pdf"))['href'].replace('../..','http://www.dpm.tn')
		index='notice'
		object.update({index : valeur})
	json_output.append(object)

print("writing to medicaments.js")
json_final = json.dumps(json_output, sort_keys=False,ensure_ascii=False)
open("medicaments.js","w").write("data="+json_final)

print("writing to autocomplete.js")
json_final = json.dumps(autocomplete, sort_keys=False,ensure_ascii=False)
open("autocomplete.js","w").write("autocomplete_list="+json_final)
