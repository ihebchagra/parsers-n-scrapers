#!/usr/bin/python
import json


dictionnary = json.load(open("dict.json"))
obj = json.load(open("pathologies.json"))
json_output={}
i=0
j=0

#key translator
for key in obj:
	entry = obj[key]
	arguments = entry['arguments']
	new_arguments = {}
	new_entry = entry
	for arg in arguments:
		if arg in dictionnary:
			j+=1
			new_arguments[dictionnary[arg]] = arguments[arg]
		else:
			if j>0:
				print('skipped arguments:',j)
				j=0
			val = ''
			while val=='':
				val = input('"' + arg + '" in french : ')
			dictionnary[arg]=val
			dict_text = json.dumps(dictionnary, sort_keys=False, indent=2, ensure_ascii=False)
			open("dict.json","w").write(dict_text)
			new_arguments[dictionnary[arg]] = arguments[arg]
	new_entry['arguments']=new_arguments
	if key in dictionnary:
		i+=1
		json_output[dictionnary[key]] = new_entry
	else:
		if i>0:
			print('skipped:',i)
			i=0
		val=''
		while val=='':
			val = input('translation for "' + key +'" : ')
		dictionnary[key] = val
		dict_text = json.dumps(dictionnary, sort_keys=False, indent=2, ensure_ascii=False)
		open("dict.json","w").write(dict_text)
		json_output[val] = new_entry

if i>0:
	print('skipped:',i)
if j>0:
	print('skipped arguments:',j)
	

print("writing to database.json")
json_final = json.dumps(json_output, sort_keys=True, indent=2, ensure_ascii=False)
open("database.json","w").write(json_final)

print("writing to database.js")
json_final = json.dumps(json_output, sort_keys=True, indent=None, ensure_ascii=False)
open("database.js","w").write('data=' + json_final)
