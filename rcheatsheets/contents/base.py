import os

import PyPDF2
import slugify
from logzero import logger

import settings


class ContentBlock:
    def __init__(self, name: str, path: str, page_width, page_height):
        self.name = slugify.slugify(name.replace('%20', ' '))
        self.path = path
        self.page_size = (page_width, page_height)
        self.page_size_mm = (
            settings.POINTS_TO_MM * page_width,
            settings.POINTS_TO_MM * page_height,
        )

    @property
    def contents(self):
        return PyPDF2.PdfFileReader(self.path, 'rb')

    def scale(self):
        logger.debug(f'Scaling {self} to {self.page_size}pt')
        writer = PyPDF2.PdfFileWriter()
        for page in self.contents.pages:
            page.scaleTo(*self.page_size)
            writer.addPage(page)
        with open(self.path, 'wb') as f:
            writer.write(f)

    def __str__(self):
        return self.name

    def __len__(self):
        return self.contents.getNumPages()

    def __del__(self):
        os.remove(self.path)
