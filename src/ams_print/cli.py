import typer

from .ams_print import ams_print


app = typer.Typer()
app.command()(ams_print)

if __name__ == "__main__":
    app()
