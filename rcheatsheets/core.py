import os
import re
import tempfile
from itertools import islice
from pathlib import Path

import pikepdf
import PyPDF2
import requests
from bs4 import BeautifulSoup
from logzero import logger

import settings
from rcheatsheets.utils import is_valid_response


class RCheatSheet:
    def __init__(self, url, output_dir):
        self.url = url
        filename = url.split('/')[-1]
        output_path = os.path.join(output_dir, filename)
        self.file = Path(output_path)
        self.path = str(self.file)

    @property
    def github_raw_url(self):
        regex = (
            r'^https?://github.com/(?P<username>[A-Za-z_-]+)/'
            r'(?P<project>[A-Za-z_-]+)/blob/(?P<path>.*)'
        )
        if m := re.search(regex, self.url):
            return (
                'https://raw.githubusercontent.com/'
                f'{m["username"]}/{m["project"]}/{m["path"]}'
            )

    def download(self):
        logger.debug(self.url)
        response = requests.get(self.url)
        valid_response, msg = is_valid_response(response)
        if valid_response:
            with self.file.open('wb') as f:
                f.write(response.content)
            return True
        else:
            logger.error(msg)
            if url := self.github_raw_url:
                logger.warning('Building new url')
                self.url = url
                self.download()
            return False

    def repair(self):
        '''https://github.com/mstamy2/PyPDF2/issues/183#issuecomment-897334512'''
        logger.warning(f'Repairing {self}')
        pdf = pikepdf.open(self.path, allow_overwriting_input=True)
        pdf.save(self.path)

    def read_pdf(self):
        try:
            return PyPDF2.PdfFileReader(self.path, 'rb')
        except PyPDF2.utils.PdfReadError:
            self.repair()
            return PyPDF2.PdfFileReader(self.path, 'rb')

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
        logger.info('Downloading cheatsheets')
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, features='html.parser')
        download_links = soup.find_all('a', string='Download')
        for link in download_links:
            if (url := link['href']).endswith('.pdf'):
                # if url.endswith('base-r.pdf'):
                yield url

    def merge_cheatsheets(self):
        logger.info('Merging cheatsheets')
        merged_file = PyPDF2.PdfFileMerger()
        for rcs in self.cheatsheets:
            logger.debug(rcs)
            # if str(rcs).endswith('base-r.pdf'):
            try:
                merged_file.append(rcs.read_pdf())
            except ValueError:
                rcs.repair()
                merged_file.append(rcs.read_pdf())

        logger.debug(f'Writing compilation book to {self.book}')
        merged_file.write(str(self.book))

    def build(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            for url in islice(self.get_cheatsheet_links(), self.max_cheatsheets):
                rcs = RCheatSheet(url, tmpdirname)
                if rcs.download():
                    self.cheatsheets.append(rcs)
            self.merge_cheatsheets()
