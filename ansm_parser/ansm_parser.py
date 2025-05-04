#!/usr/bin/python

# print(element.x0,element.get_text())
# DCI = 29
# interaction = 32
# useless data = 36
# effet indésirable = 97
# niveau contre indication = 317


from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from math import floor
import json

database = []
autocomplete = []
obj = {}
interact_obj={}
page=0

for page_layout in extract_pages('ansm.pdf'):
	page+=1
	print('processing page',page)
	for element in page_layout:
		if isinstance(element, LTTextContainer):
				if floor(element.x0) == 29 :
					if len(obj) != 0:
						if len(interact_obj['substance'])==0:
							obj['substance']+=element.get_text().replace('\n',' ')
							continue
						else:
							obj['interactions'].append(interact_obj)
							database.append(obj)
					obj={}
					obj['substance']=element.get_text().replace('\n','')
					autocomplete.append(element.get_text().replace('\n',''))
					obj['interactions']=[]
					interact_obj={}
					interact_obj['substance']=''
					interact_obj['effet']=''
					interact_obj['indication']=''
				elif floor(element.x0) == 32 :
					if len(interact_obj['substance']) != 0:
						if( (interact_obj['indication']=='') and (interact_obj['effet']=='')):
							interact_obj['substance']+=element.get_text().replace('\n','').replace('+ ',' ')
							continue
						else:
							obj['interactions'].append(interact_obj)
					interact_obj={}
					interact_obj['substance']=element.get_text().replace('\n','').replace('+ ','')
					interact_obj['effet']=''
					interact_obj['indication']=''
				elif floor(element.x0) == 97 :
					interact_obj['effet']+=element.get_text().replace('\n',' ')
				elif floor(element.x0) == 317 :
					interact_obj['indication']+=element.get_text().replace('\n',' ')

obj['interactions'].append(interact_obj)
database.append(obj)
			


print("writing to interactions.js")
json_final = json.dumps(database, sort_keys=False, indent=None, ensure_ascii=False)
open("interactions.js","w").write("data="+json_final)


print("writing to autocomplete.js")
json_final = json.dumps(autocomplete, sort_keys=False, indent=None, ensure_ascii=False)
open("autocomplete.js","w").write("autocomplete_list="+json_final)
