#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import re
import os


try:
	os.mkdir("pages_downloaded")
except:
	print("spec directory already created")

try:
	os.mkdir("pages_downloaded_sup")
except:
	print("sup already created")

try:
	os.mkdir("pages_downloaded_sus")
except:
	print("sus already created")




print('downloading suspendus')
html_doc=open("dpmsus.html")
soup = BeautifulSoup(html_doc, 'html.parser')
num_medic=len(soup.find_all('a',href=re.compile('fiche\.php')))
i=0
for link in soup.find_all('a',href=re.compile('fiche\.php')):
	i=i+1
	cod_medic=link['href'].replace('fiche.php?cod_medic=','')
	print('getting', i, '/', num_medic)
	url=f'http://www.dpm.tn/dpm_pharm/medicament/fiche.php?cod_medic={cod_medic}'
	r = requests.get(url, allow_redirects=True)
	open(f"pages_downloaded_sus/{cod_medic}.html","wb").write(r.content)


print('downloading supprimés')
html_doc=open("dpmsup.html")
soup = BeautifulSoup(html_doc, 'html.parser')
num_medic=len(soup.find_all('a',href=re.compile('fiche2\.php')))
i=0
for link in soup.find_all('a',href=re.compile('fiche2\.php')):
	i=i+1
	cod_medic=link['href'].replace('fiche2.php?cod_medic=','')
	print('getting', i, '/', num_medic)
	url=f'http://www.dpm.tn/dpm_pharm/medicament/fiche2.php?cod_medic={cod_medic}'
	r = requests.get(url, allow_redirects=True)
	open(f"pages_downloaded_sup/{cod_medic}.html","wb").write(r.content)




print('downloading spécialité')
html_doc=open("dpm.html")
soup = BeautifulSoup(html_doc, 'html.parser')
num_medic=len(soup.find_all('a',href=re.compile('fiche\.php')))
i=0
for link in soup.find_all('a',href=re.compile('fiche\.php')):
	i=i+1
	cod_medic=link['href'].replace('fiche.php?cod_medic=','')
	print('getting', i, '/', num_medic)
	url=f'http://www.dpm.tn/dpm_pharm/medicament/fiche.php?cod_medic={cod_medic}'
	r = requests.get(url, allow_redirects=True)
	open(f"pages_downloaded/{cod_medic}.html","wb").write(r.content)

