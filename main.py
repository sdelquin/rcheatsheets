from pathlib import Path

import typer

import settings
from rcheatsheets.core import Handler

app = typer.Typer(add_completion=False)


@app.command()
def run(
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
    handler = Handler(book_path=book_path, max_cheatsheets=max_cheatsheets)
    handler.build()


if __name__ == '__main__':
    app()
