import datetime
import os
import shutil
from pathlib import Path

import PyPDF2
from logzero import logger
from reportlab.pdfgen import canvas

import settings
from rcheatsheets.contents.base import ContentBlock
from rcheatsheets.utils import mk_tmpfile


class Cover(ContentBlock):
    def __init__(
        self,
        file: Path,
        page_width=settings.PAGE_WIDTH,
        page_height=settings.PAGE_HEIGHT,
    ):
        tmpfile = mk_tmpfile()
        path = shutil.copy(file, tmpfile)
        super().__init__('cover', path, page_width, page_height)

    def make_last_update_page(
        self, timestamp, last_update_xpos, last_update_ypos, fontsize
    ):
        tmpfile = mk_tmpfile()
        c = canvas.Canvas(tmpfile)
        c.setPageSize(self.page_size)
        c.setFontSize(fontsize)
        text = f'Last update: {timestamp.isoformat()}'
        c.drawString(last_update_xpos, last_update_ypos, text)
        c.save()
        contents = PyPDF2.PdfFileReader(tmpfile)
        os.remove(tmpfile)
        return contents

    def add_timestamp(
        self,
        timestamp=datetime.date.today(),
        last_update_xpos=settings.LAST_UPDATE_XPOS,
        last_update_ypos=settings.LAST_UPDATE_YPOS,
        fontsize=settings.LAST_UPDATE_FONTSIZE,
    ):
        logger.debug('Adding timestamp for last update')
        writer = PyPDF2.PdfFileWriter()
        marked_contents = self.make_last_update_page(
            timestamp, last_update_xpos, last_update_ypos, fontsize
        )
        for page, marked_page in zip(self.contents.pages, marked_contents.pages):
            page.mergePage(marked_page)
            writer.addPage(page)
        with open(self.path, 'wb') as f:
            writer.write(f)
