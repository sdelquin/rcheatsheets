from pathlib import Path

from prettyconf import config

PROJECT_DIR = Path(__file__).parent.resolve()
PROJECT_NAME = PROJECT_DIR.name

CHEATSHEETS_URL = config(
    'CHEATSHEETS_URL', default='https://github.com/rstudio/cheatsheets'
)
GITHUB_BASE_URL = config(
    'GITHUB_BASE_URL',
    default='https://raw.githubusercontent.com/rstudio/cheatsheets/main/',
)
BOOK_PATH = config('BOOK_PATH', default=PROJECT_DIR / (PROJECT_NAME + '.pdf'), cast=Path)
CHEATSHEET_BLACKLIST = config('CHEATSHEET_BLACKLIST', default=[], cast=config.list)

LOGFILE = config('LOGFILE', default=PROJECT_DIR / (PROJECT_NAME + '.log'), cast=Path)
LOGFILE_SIZE = config('LOGFILE_SIZE', cast=float, default=1e6)
LOGFILE_BACKUP_COUNT = config('LOGFILE_BACKUP_COUNT', cast=int, default=3)

# Dimensions (in points) for each page on output compilation book
# A4 aspect ratio = 0.7
PAGE_WIDTH = config('PAGE_WIDTH', default=1100, cast=int)
PAGE_HEIGHT = config('PAGE_HEIGHT', default=770, cast=int)

# Position (in points) where the page number will be written
PAGENUMBER_XPOS = config('PAGENUMBER_XPOS', default=PAGE_WIDTH - 25, cast=int)
PAGENUMBER_YPOS = config('PAGENUMBER_YPOS', default=25, cast=int)

PAGENUMBER_FONTSIZE = config('PAGENUMBER_FONTSIZE', default=16, cast=int)

# Initial position (in points) where TOC contents will be written
TOC_CONTENTS_XPOS = config('TOC_CONTENTS_XPOS', default=100, cast=int)
TOC_CONTENTS_YPOS = config('TOC_CONTENTS_YPOS', default=PAGE_HEIGHT - 100, cast=int)

TOC_COLUMNS = config('TOC_COLUMNS', default=3)
TOC_ITEMS_PER_COLUMN = config('TOC_ITEMS_PER_COLUMN', default=30, cast=int)
TOC_MARGIN_TOP = config('TOC_MARGIN_TOP', default=2, cast=int)
TOC_COL_CHARS = config('TOC_COL_CHARS', default=26, cast=int)

# Properties of last update message on cover
LAST_UPDATE_XPOS = config('LAST_UPDATE_XPOS', default=75, cast=int)
LAST_UPDATE_YPOS = config('LAST_UPDATE_YPOS', default=110, cast=int)
LAST_UPDATE_FONTSIZE = config('LAST_UPDATE_FONTSIZE', default=18, cast=int)

COVER_PATH = config('COVER_PATH', default=PROJECT_DIR / 'cover.pdf', cast=Path)

POINTS_TO_MM = config('POINTS_TO_MM', default=0.352777778)
