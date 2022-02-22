import os
import tempfile
from pathlib import Path

import PyPDF2
import requests
from bs4 import BeautifulSoup

URL = 'https://www.rstudio.com/resources/cheatsheets/'


def get_cheatsheet_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features='html.parser')
    download_links = soup.find_all('a', string='Download')
    for link in download_links:
        if (url := link['href']).endswith('.pdf'):
            yield url


def download_cheatsheet(url, output_dir):
    response = requests.get(url)
    filename = response.url.split('/')[-1]
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'wb') as f:
        f.write(response.content)


def merge_cheatsheets(dir):
    merged_file = PyPDF2.PdfFileMerger()
    for f in Path(dir).iterdir():
        merged_file.append(PyPDF2.PdfFileReader(str(f), 'rb'))
    merged_file.write('rcheatsheets.pdf')


with tempfile.TemporaryDirectory() as tmpdirname:
    for url in get_cheatsheet_links(URL):
        download_cheatsheet(url, tmpdirname)
    merge_cheatsheets(tmpdirname)
