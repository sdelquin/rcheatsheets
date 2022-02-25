import os
import re

import pikepdf
import PyPDF2
import requests
from logzero import logger
from reportlab.pdfgen import canvas

import settings
from rcheatsheets.contents.base import ContentBlock
from rcheatsheets.utils import is_valid_response, mk_tmpfile


class CheatSheet(ContentBlock):
    def __init__(
        self,
        url: str = None,
        starting_pagenumber=1,
        page_width=settings.PAGE_WIDTH,
        page_height=settings.PAGE_HEIGHT,
        pagenumber_xpos=settings.PAGENUMBER_XPOS,
        pagenumber_ypos=settings.PAGENUMBER_YPOS,
        pagenumber_fontsize=settings.PAGENUMBER_FONTSIZE,
    ):
        self.url = url
        name = url.split('/')[-1].split('.')[0]
        path = mk_tmpfile()
        super().__init__(name, path, page_width, page_height)

        self.starting_pagenumber = starting_pagenumber
        self.pagenumber_pos = (pagenumber_xpos, pagenumber_ypos)
        self.pagenumer_fontsize = pagenumber_fontsize

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

    def stage(self):
        logger.info(f'Staging {self}')
        self.repair()
        self.scale()
        self.add_page_numbers()

    def get_numbered_contents(self):
        tmpfile = mk_tmpfile()
        c = canvas.Canvas(tmpfile)
        for i in range(len(self)):
            pagenumber = self.starting_pagenumber + i
            c.setPageSize(self.page_size)
            c.setFontSize(self.pagenumer_fontsize)
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
