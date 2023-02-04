import typer
from rich import print

from typing import Optional

from functionalflows.config import setup
from functionalflows import __app_name__, __version__


app = typer.Typer()

@app.command()
def run(config_filepath: str = typer.Option(..., '---config', '-c', help='String path to .toml configuration file containing component definitions.'),  
        input_filepath: str = typer.Option(..., '--inputs', '-i', help='String path to .csv file containing timeseries of dates and flows. Expects to find \"date\" and \"flow\" column labels in row 0.'),
        output_filepath: str = typer.Option('', '--outputs', '-o', help='Target string path for .csv output files.')):
    analysis = setup(config_filepath, input_filepath)
    return analysis.run(output_path=output_filepath)

@app.command()
def main(version: Optional[bool] = typer.Option(None, '--version',  '-v', help='Show application version and exit.', is_eager=True)):
    if version:
        print(f'{__app_name__} v{__version__}')
        raise typer.Exit()

if __name__ == '__main__':
    app(prog_name=__app_name__)