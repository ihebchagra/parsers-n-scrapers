#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import re
import os

url = 'https://www.medecinesfax.org/fra/s174/pages/66/Examen-classant-national'
print("getting the list")
r = requests.get(url, allow_redirects=True)
soup = BeautifulSoup(r.content, 'html.parser')


try:
	os.mkdir("pdfs")
except:
	print("directory already created")

accordion = soup.find('div',id='Accordion2Content')

for i in accordion.childGenerator():
	if i.name=='a':
		filename = 'pdfs/' + i.text.replace('Télécharger Sujet :','').strip() + '.pdf'
		url = 'https://www.medecinesfax.org' + i.attrs['href']
		print('downloading',filename)
		r = requests.get(url, allow_redirects=True)
		open(filename,'wb').write(r.content)
	elif i.name=='h3' and i.text.strip()=='':
		break
