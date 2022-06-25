#!/usr/bin/python
import json

json_output={}
cache = json.load(open("cache.json"))
n=0

f="database.json"
obj = json.load(open(f))

for i in obj:
	if 'sex' not in obj[i]:
		if i in cache:
			n+=1
			json_output[i] = {**obj[i], 'sex':cache[i]}
		else:
			if n>0:
				print('skipped ',n)
				n=0
			val = ''
			while val not in ['M','F']:
				val = input('Sex for "' + i + '" [M/F]: ').upper()
			cache[i]=val
			cache_text = json.dumps(cache, sort_keys=False, indent=2, ensure_ascii=False)
			open("cache.json","w").write(cache_text)
			json_output[i] = {**obj[i], 'sex':val}
	else:
		json_output[i] = {**obj[i]}
		
	


print("writing to pathologies.json")
json_final = json.dumps(json_output, sort_keys=False, indent=2, ensure_ascii=False)
open("pathologies.json","w").write(json_final)
