import shutil
from pathlib import Path

import settings
from rcheatsheets.contents.base import ContentBlock
from rcheatsheets.utils import mk_tmpfile


class Cover(ContentBlock):
    def __init__(
        self, file: Path, page_width=settings.PAGE_WIDTH, page_height=settings.PAGE_HEIGHT
    ):
        tmpfile = mk_tmpfile()
        path = shutil.copy(file, tmpfile)
        super().__init__('cover', path, page_width, page_height)
