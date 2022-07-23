#!/usr/bin/python

import json
import csv



print("loading csv file")
reader = csv.reader(open('liste.csv', mode='r'))
	

autocomplete = []
json_output=[]
i=0
for rows in reader:
	i=i+1
	if i==1:
		continue
	object = {
		"Spécialité": rows[0],
		"Dosage": rows[1],
		"Forme": rows[2],
		"Présentation": rows[3],
		"DCI": rows[4],
		"Classe": rows[5],
		"Sous Classe": rows[6],
		"Laboratoire": rows[7],
		"AMM": rows[8],
		"Date AMM": rows[9],
		"Conditionnement primaire": rows[10],
		"Spécification Conditionnement primaire": rows[11],
		"Tableau": rows[12],
		"Durée de conservation": rows[13],
		"Indications": rows[14],
		"G/P/B": rows[15],
		"VEIC": rows[16] }
	todelete=[]
	for j in object:
		if object[j]=="":
			todelete.append(j)
	for j in todelete:
		_ = object.pop(j,None)
	if ((rows[0] not in autocomplete) and (rows[0]!="")):
			autocomplete.append(rows[0])
	if ((rows[4] not in autocomplete) and (rows[4]!="")):
			autocomplete.append(rows[4])
	json_output.append(object)

print("writing to medicaments.js")
json_final = json.dumps(json_output, sort_keys=False,ensure_ascii=False)
open("medicaments.js","w").write("data="+json_final)

print("writing to autocomplete.js")
json_final = json.dumps(autocomplete, sort_keys=True,ensure_ascii=False)
open("autocomplete.js","w").write("autocomplete_list="+json_final)
