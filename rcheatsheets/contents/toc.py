from fpdf import FPDF, HTMLMixin

import settings
from rcheatsheets.contents.base import ContentBlock
from rcheatsheets.contents.cheatsheet import CheatSheet
from rcheatsheets.utils import mk_tmpfile


class PDF(FPDF, HTMLMixin):
    pass


class TOC(ContentBlock):
    def __init__(
        self,
        cheatsheets: list[CheatSheet],
        /,
        page_width=settings.PAGE_WIDTH,
        page_height=settings.PAGE_HEIGHT,
        content_xpos=settings.TOC_CONTENTS_XPOS,
        content_ypos=settings.TOC_CONTENTS_YPOS,
        columns=settings.TOC_COLUMNS,
        items_per_column=settings.TOC_ITEMS_PER_COLUMN,
        col_chars=settings.TOC_COL_CHARS,
        margin_top=settings.TOC_MARGIN_TOP,
    ):
        self.cheatsheets = cheatsheets
        name = 'TOC'
        path = mk_tmpfile()

        super().__init__(name, path, page_width, page_height)

        self.content_pos = (content_xpos, content_ypos)
        self.columns = columns
        self.colwidth = 100 // columns
        self.items_per_column = items_per_column
        self.margin_top = margin_top
        self.col_chars = col_chars

        self.build()

    def build(self):
        pdf = PDF(orientation='landscape', format='A4')
        pdf.set_top_margin(self.margin_top)
        pdf.set_font('Courier')
        pdf.add_page()

        buffer = []

        buffer.append('<h1>Table of contents</h1>')
        buffer.append('<br>')
        buffer.append('<table>')
        for row in range(self.items_per_column):
            buffer.append('<tr>')
            for col in range(self.columns):
                index = col * self.items_per_column + row
                if index >= len(self.cheatsheets):
                    break
                cheatsheet = self.cheatsheets[index]
                name = cheatsheet.name[: self.col_chars - 2]
                dots = '.' * (self.col_chars - len(name))
                page = cheatsheet.starting_pagenumber
                buffer.append(f'<td width="{self.colwidth}%">{name}{dots}{page}</td>')
            buffer.append('</tr>')

        html = '\n'.join(buffer)
        pdf.write_html(html)
        pdf.output(self.path)
