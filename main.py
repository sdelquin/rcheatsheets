from pathlib import Path

import logzero
import typer

import settings
from rcheatsheets.core import Handler
from rcheatsheets.utils import init_logger

app = typer.Typer(add_completion=False)
logger = init_logger()


@app.command()
def run(
    verbose: bool = typer.Option(
        False, '--verbose', '-v', show_default=False, help='Loglevel increased to debug.'
    ),
    book_path: Path = typer.Option(
        settings.BOOK_PATH,
        '--output',
        '-o',
        help='Output path for the compilation book.',
    ),
    max_cheatsheets: int = typer.Option(
        None,
        '--max-cheatsheets',
        '-m',
        help='Max number of cheatsheets to be compiled.',
    ),
):
    logger.setLevel(logzero.DEBUG if verbose else logzero.INFO)

    handler = Handler(book_path=book_path)
    handler.build(max_cheatsheets)


if __name__ == '__main__':
    app()
