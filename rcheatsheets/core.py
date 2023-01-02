import re
from itertools import islice
from pathlib import Path

import PyPDF2
import requests
from bs4 import BeautifulSoup
from logzero import logger

import settings
from rcheatsheets.contents.cheatsheet import CheatSheet
from rcheatsheets.contents.cover import Cover
from rcheatsheets.contents.toc import TOC


class Handler:
    def __init__(self, url=settings.CHEATSHEETS_URL, book_path=settings.BOOK_PATH):
        self.url = url
        self.book = Path(book_path)
        self.cheatsheets = []

    def get_cheatsheet_links(self):
        logger.info('Downloading cheatsheets')
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, features='html.parser')
        a_entries = soup.find_all('a', 'Link--primary', href=re.compile(r'^.*\.pdf$'))
        for a in a_entries:
            yield settings.GITHUB_BASE_URL + Path(a['href']).name

    def make_cover(self, cover_path=settings.COVER_PATH):
        logger.info('Making cover')
        self.cover = Cover(cover_path)
        self.cover.scale()
        self.cover.add_timestamp()

    def make_toc(self):
        logger.info('Making table of contents')
        self.toc = TOC(self.cheatsheets)
        self.toc.scale()

    def merge_contents(self):
        logger.info('Merging contents')
        merged_file = PyPDF2.PdfFileMerger()
        merged_file.append(self.cover.contents)
        merged_file.append(self.toc.contents)
        for sheet in self.cheatsheets:
            merged_file.append(sheet.contents)

        logger.info(f'Writing compilation book to {self.book}')
        merged_file.write(str(self.book))

    def build(self, max_cheatsheets=None):
        logger.info('Building compilation book')

        cheatsheets = [
            CheatSheet(url) for url in islice(self.get_cheatsheet_links(), max_cheatsheets)
        ]
        cheatsheets.sort(key=lambda c: c.name)

        current_page = 1
        for sheet in cheatsheets:
            if sheet.download():
                sheet.repair()
                sheet.scale()
                sheet.add_page_numbers(current_page)
                self.cheatsheets.append(sheet)
                current_page += len(sheet)

        self.make_cover()
        self.make_toc()
        self.merge_contents()
