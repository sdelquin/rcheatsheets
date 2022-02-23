import os
import tempfile
from itertools import islice
from pathlib import Path

import PyPDF2
import requests
from bs4 import BeautifulSoup
from logzero import logger

import settings


class RCheatSheet:
    def __init__(self, url, output_dir):
        logger.debug(url)
        response = requests.get(url)
        filename = response.url.split('/')[-1]
        output_path = os.path.join(output_dir, filename)
        self.file = Path(output_path)
        with self.file.open('wb') as f:
            f.write(response.content)

    def read_pdf(self):
        return PyPDF2.PdfFileReader(str(self.file), 'rb')

    def __str__(self):
        return self.file.name


class Handler:
    def __init__(
        self,
        url=settings.CHEATSHEETS_URL,
        book_path=settings.BOOK_PATH,
        max_cheatsheets=None,
    ):
        self.url = url
        self.book = Path(book_path)
        self.cheatsheets = []
        self.max_cheatsheets = max_cheatsheets

    def get_cheatsheet_links(self):
        logger.info('Getting cheatsheets links')
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, features='html.parser')
        download_links = soup.find_all('a', string='Download')
        for link in download_links:
            if (url := link['href']).endswith('.pdf'):
                yield url

    def merge_cheatsheets(self):
        logger.info('Merging cheatsheets')
        merged_file = PyPDF2.PdfFileMerger()
        for rcs in self.cheatsheets:
            logger.debug(rcs)
            merged_file.append(rcs.read_pdf())
        logger.debug(f'Writing compilation book to {self.book}')
        merged_file.write(str(self.book))

    def build(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            logger.info('Downloading cheatsheets')
            for url in islice(self.get_cheatsheet_links(), self.max_cheatsheets):
                self.cheatsheets.append(RCheatSheet(url, tmpdirname))
            self.merge_cheatsheets()
