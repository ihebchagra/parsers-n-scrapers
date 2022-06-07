#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import re
import os

url = 'http://www.phct.com.tn/index.php/medicaments-humain?resetfilters=0&clearordering=0&clearfilters=0&limitstart22=0&limit22=100'
print("checking number of pages")
r = requests.get(url, allow_redirects=True)
soup = BeautifulSoup(r.content, 'html.parser')
pages=int(soup.find("small",text=re.compile("Page 1 sur")).string.strip().replace("Page 1 sur ",""))
print(pages, "pages detected")

try:
	os.mkdir("pages_downloaded")
except:
	print("directory already created")

for i in range(0,pages):
	url=f"http://www.phct.com.tn/index.php/medicaments-humain?resetfilters=0&clearordering=0&clearfilters=0&limit22=100&limitstart22={i*100}"
	print(f"downloading page {i+1}")
	r = requests.get(url,allow_redirects=True)	
	open(f"pages_downloaded/{i}.html","wb").write(r.content)
