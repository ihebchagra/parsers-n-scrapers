#!/usr/bin/python
import json


obj = json.load(open("database.json"))
json_output=[]

#key translator
for key in obj:
	arguments = obj[key]['arguments']
	for arg in arguments:
		if arg not in json_output:
			json_output.append(arg)

print('detected ',len(json_output))
	
print("writing to arguments.js")
json_final = json.dumps(json_output, sort_keys=True, indent=None, ensure_ascii=False)
open("arguments.js","w").write('argument_list=' + json_final)
