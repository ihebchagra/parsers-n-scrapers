#!/usr/bin/python

from bs4 import BeautifulSoup
import re
import os
import json

autocomplete = []
json_output=[]

#for h in [['dpm.html','pages_downloaded'],['dpmsup.html','pages_downloaded_sup']]:
for h in [['dpm.html','pages_downloaded']]:
	html_doc=open(h[0],encoding='utf-8')
	print("loading " + h[0] + " file")
	bigsoup=BeautifulSoup(html_doc, 'html.parser')
	html_doc.close()
	directory=h[1]
	i=0
	length=len(os.listdir(directory))
	for filename in os.listdir(directory):
		i=i+1
		print("fetching médicament ",i,"/",length)
		f = os.path.join(directory, filename)
		if not os.path.isfile(f):
			continue
		fiche = open(f,encoding='utf-8')
		soup = BeautifulSoup(fiche, 'html.parser')
		fiche.close()
		object = {}
		for entry in soup.find_all("tr"):
			if entry.find("b") is None:
				continue
			if entry.find_all('td')[1].font.string is None:
				continue
			index=next(entry.b.strings).replace(" :","").replace(" ","")
			valeur=entry.find_all('td')[1].font.string.replace("\n"," ")
			if index in ['DCI','Spécialité']:
				if valeur not in autocomplete:
					autocomplete.append(valeur)
			object.update({index : valeur})
		try:
			bigparent=bigsoup.find(string=re.compile(object['AMM'])).parent.parent
			if bigparent.find('a',href=re.compile("rcp.pdf")) is not None:
				valeur=bigparent.find('a',href=re.compile("rcp.pdf"))['href'].replace('../..','http://www.dpm.tn')
				index='rcp'
				object.update({index : valeur})
			if bigparent.find('a',href=re.compile("notice.pdf")) is not None:
				valeur=bigparent.find('a',href=re.compile("notice.pdf"))['href'].replace('../..','http://www.dpm.tn')
				index='notice'
				object.update({index : valeur})
		except:
			print("no AMM")
		json_output.append(object)

print("writing to medicaments.js")
json_final = json.dumps(json_output, sort_keys=False,ensure_ascii=False)
open("medicaments.js","w",encoding='utf-8').write("data="+json_final)

print("writing to autocomplete.js")
json_final = json.dumps(autocomplete, sort_keys=False,ensure_ascii=False)
open("autocomplete.js","w",encoding='utf-8').write("autocomplete_list="+json_final)
