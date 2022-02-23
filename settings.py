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
