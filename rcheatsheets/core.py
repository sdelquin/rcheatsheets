import os
import re
import shutil
from itertools import islice
from pathlib import Path

import pikepdf
import PyPDF2
import requests
from bs4 import BeautifulSoup
from logzero import logger
from reportlab.pdfgen import canvas

import settings
from rcheatsheets.utils import is_valid_response, mk_tmpfile


class RCheatSheet:
    def __init__(
        self,
        /,
        file: Path = None,
        url: str = None,
        starting_pagenumber=1,
        page_width=settings.PAGE_WIDTH,
        page_height=settings.PAGE_HEIGHT,
        pagenumber_xpos=settings.PAGENUMBER_XPOS,
        pagenumber_ypos=settings.PAGENUMBER_YPOS,
    ):
        '''Available invocations:
        - RCheatSheet(file='foo.pdf')
        - RCheatSheet(url='https://example.com/bar.pdf')

        If starting_pagenumber is None, page numbers are not written.
        '''
        self.path = mk_tmpfile()
        if file:
            self.name = file.name
            shutil.copy(file, self.path)
        else:
            self.url = url
            self.name = url.split('/')[-1]
        self.name = self.name.split('.')[0]

        self.starting_pagenumber = starting_pagenumber
        self.page_size = (page_width, page_height)
        self.pagenumber_pos = (pagenumber_xpos, pagenumber_ypos)

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
            with open(self.path, 'wb') as f:
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
        logger.debug(f'Repairing {self}')
        pdf = pikepdf.open(self.path, allow_overwriting_input=True)
        pdf.save(self.path)

    @property
    def contents(self):
        return PyPDF2.PdfFileReader(self.path, 'rb')

    def scale(self, width, height):
        logger.debug(f'Scaling {self} to {width}x{height}')
        writer = PyPDF2.PdfFileWriter()
        for page in self.contents.pages:
            page.scaleTo(width, height)
            writer.addPage(page)
        with open(self.path, 'wb') as f:
            writer.write(f)

    def stage(self):
        logger.info(f'Staging {self}')
        self.repair()
        self.scale(*self.page_size)
        if self.starting_pagenumber is not None:
            self.add_page_numbers()

    def get_numbered_contents(self):
        tmpfile = mk_tmpfile()
        c = canvas.Canvas(tmpfile)
        for i in range(len(self)):
            pagenumber = self.starting_pagenumber + i
            c.setPageSize(self.page_size)
            c.setFontSize(settings.PAGENUMBER_FONTSIZE)
            c.drawString(*self.pagenumber_pos, str(pagenumber))
            c.showPage()
        c.save()
        contents = PyPDF2.PdfFileReader(tmpfile)
        os.remove(tmpfile)
        return contents

    def add_page_numbers(self):
        logger.debug('Adding page numbers')
        writer = PyPDF2.PdfFileWriter()
        numbered_contents = self.get_numbered_contents()
        for page, numbered_page in zip(self.contents.pages, numbered_contents.pages):
            page.mergePage(numbered_page)
            writer.addPage(page)
        with open(self.path, 'wb') as f:
            writer.write(f)

    def __str__(self):
        return self.name

    def __del__(self):
        os.remove(self.path)
        if getattr(self, 'numbered_path', None):
            os.remove(self.numbered_path)

    def __len__(self):
        return self.contents.getNumPages()


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

    def add_cover(self, cover_path=settings.COVER_PATH):
        logger.debug('Adding cover')
        cover = RCheatSheet(file=cover_path, starting_pagenumber=None)
        self.cheatsheets.append(cover)

    def merge_cheatsheets(self):
        logger.info('Merging cheatsheets')
        merged_file = PyPDF2.PdfFileMerger()
        for rcs in self.cheatsheets:
            rcs.stage()
            merged_file.append(rcs.contents)

        logger.info(f'Writing compilation book to {self.book}')
        merged_file.write(str(self.book))

    def build(self):
        logger.info('Building compilation book')
        self.add_cover()
        current_page = 1
        for url in islice(self.get_cheatsheet_links(), self.max_cheatsheets):
            rcs = RCheatSheet(url=url, starting_pagenumber=current_page)
            if rcs.download():
                self.cheatsheets.append(rcs)
                current_page += len(rcs)
        self.merge_cheatsheets()
