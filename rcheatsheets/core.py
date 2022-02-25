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
                yield url

    def make_cover(self, cover_path=settings.COVER_PATH):
        logger.debug('Making cover')
        self.cover = Cover(cover_path)
        self.cover.scale()

    def make_toc(self):
        logger.debug('Making TOC')
        self.toc = TOC(self.cheatsheets)
        self.toc.scale()

    def merge_contents(self):
        logger.info('Merging contents')
        merged_file = PyPDF2.PdfFileMerger()
        merged_file.append(self.cover.contents)
        merged_file.append(self.toc.contents)
        for rcs in self.cheatsheets:
            merged_file.append(rcs.contents)

        logger.info(f'Writing compilation book to {self.book}')
        merged_file.write(str(self.book))

    def build(self):
        logger.info('Building compilation book')

        current_page = 1
        for url in islice(self.get_cheatsheet_links(), self.max_cheatsheets):
            rcs = CheatSheet(url=url, starting_pagenumber=current_page)
            if rcs.download():
                rcs.stage()
                self.cheatsheets.append(rcs)
                current_page += len(rcs)

        self.make_cover()
        self.make_toc()
        self.merge_contents()
