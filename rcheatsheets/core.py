import os
import tempfile
from itertools import islice
from pathlib import Path

import PyPDF2
import requests
from bs4 import BeautifulSoup


class RCheatSheet:
    def __init__(self, url, output_dir):
        response = requests.get(url)
        filename = response.url.split('/')[-1]
        output_path = os.path.join(output_dir, filename)
        self.file = Path(output_path)
        with self.file.open('wb') as f:
            f.write(response.content)

    def read_pdf(self):
        return PyPDF2.PdfFileReader(str(self.file), 'rb')


class Handler:
    def __init__(self, url, book_filename):
        self.url = url
        self.book = Path(book_filename)
        self.cheatsheets = []

    def get_cheatsheet_links(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, features='html.parser')
        download_links = soup.find_all('a', string='Download')
        for link in download_links:
            if (url := link['href']).endswith('.pdf'):
                yield url

    def merge_cheatsheets(self):
        merged_file = PyPDF2.PdfFileMerger()
        for rcs in self.cheatsheets:
            merged_file.append(rcs.read_pdf())
        merged_file.write(str(self.book))

    def build(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            for url in islice(self.get_cheatsheet_links(), 4):
                self.cheatsheets.append(RCheatSheet(url, tmpdirname))
            self.merge_cheatsheets()
