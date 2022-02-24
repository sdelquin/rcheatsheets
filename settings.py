from pathlib import Path

from prettyconf import config

PROJECT_DIR = Path(__file__).parent.resolve()
PROJECT_NAME = PROJECT_DIR.name

CHEATSHEETS_URL = config(
    'CHEATSHEETS_URL', default='https://www.rstudio.com/resources/cheatsheets/'
)
BOOK_PATH = config('BOOK_PATH', default=PROJECT_DIR / (PROJECT_NAME + '.pdf'), cast=Path)

LOGFILE = config('LOGFILE', default=PROJECT_DIR / (PROJECT_NAME + '.log'), cast=Path)
LOGFILE_SIZE = config('LOGFILE_SIZE', cast=float, default=1e6)
LOGFILE_BACKUP_COUNT = config('LOGFILE_BACKUP_COUNT', cast=int, default=3)

# Dimensions (in points) for each page on output compilation book
PAGE_WIDTH = config('PAGE_WIDTH', default=1100, cast=int)
PAGE_HEIGHT = config('PAGE_HEIGHT', default=850, cast=int)
# Position (in points) where the page number will be written
PAGENUMBER_XPOS = config('PAGENUMBER_XPOS', default=PAGE_WIDTH - 25, cast=int)
PAGENUMBER_YPOS = config('PAGENUMBER_YPOS', default=PAGE_HEIGHT - 25, cast=int)
PAGENUMBER_FONTSIZE = config('PAGENUMBER_FONTSIZE', default=16, cast=int)

COVER_PATH = config('COVER_PATH', default=PROJECT_DIR / 'cover.pdf', cast=Path)
