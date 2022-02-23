from pathlib import Path

from prettyconf import config

PROJECT_DIR = Path(__file__).parent.resolve()
PROJECT_NAME = PROJECT_DIR.name

CHEATSHEETS_URL = config(
    'CHEATSHEETS_URL', default='https://www.rstudio.com/resources/cheatsheets/'
)
BOOK_PATH = config('BOOK_PATH', default=PROJECT_DIR / (PROJECT_NAME + '.pdf'), cast=Path)
