import typer
from pathlib import Path
from functions import init_function, add_function, rollback_function
from helper_functions import load_config_path

app = typer.Typer(help="DeciDoc – Decision Documentation CLI")

# ------------------------
# INIT COMMAND
# ------------------------

@app.command()
def init(
    path: Path = typer.Option(..., help="Pad naar het markdown bestand"),
):
    """
    Initialiseert een nieuw keuzelog document en slaat het pad op.
    """
    init_function(path)


# ------------------------
# ADD COMMAND
# ------------------------

@app.command()
def add(
    title: str = typer.Option(..., help="Korte omschrijving van de keuze"),
    category: str = typer.Option(..., help="Categorie (Architectuur, Ontwerp, etc.)"),
    status: str = typer.Option("Definitief", help="Status van de keuze"),

    context: str = typer.Option("", help="Context van de keuze"),
    considerations: str = typer.Option("", help="Overwogen opties"),
    choice: str = typer.Option("", help="Gemaakte keuze"),
    motivation: str = typer.Option("", help="Motivatie voor de keuze"),
    reflection: str = typer.Option("", help="Eerste reflectie / leerpunt"),
    stakeholders: str = typer.Option("", help="Betrokkenen bij de keuze"),
    sources: list[str] = typer.Option(None, help="Bronverwijzing (URL of tekst) Bijv. -s 'https://www.python.org, https://www.google.com'"),

    path: Path | None = typer.Option(None, help="Optioneel: override pad"),
):
    """
    Voeg een nieuwe keuze toe aan het keuzelog.
    """
    add_function(title, category, status, context, considerations, choice, motivation, reflection, stakeholders, sources, path)


# ------------------------
# ROLLBACK COMMAND
# ------------------------

@app.command()
def rollback(
    path: Path | None = typer.Option(None, help="Optioneel: override pad"),
):
    """
    Verwijder de laatste keuze uit het keuzelog.
    """
    rollback_function(path)


# ------------------------
# SHOW CONFIG (handig)
# ------------------------

@app.command()
def config():
    """
    Toon het opgeslagen keuzelog pad.
    """
    path = load_config_path()
    if path:
        typer.echo(f"📄 Huidig keuzelog: {path}")
    else:
        typer.echo("❌ Nog geen keuzelog pad ingesteld")


def main():
    app()

if __name__ == "__main__":
    main()